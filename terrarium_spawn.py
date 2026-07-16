"""
terrarium_spawn.py (v2) — named, persistent small minds with WORKSHOPS.

Served by a local model (llama-server / Ollama, OpenAI-compatible endpoint).
Agents never see the endpoint or key; the harness makes every call.

What a mind is:
  • a JSON file under SPAWN_DIR: persona + rolling conversation history
  • a workshop folder inside the world: world/workshop_<Name>/
    (visible to all agents — no hidden machinery — but only that mind
    writes/runs there)

What a mind can DO during a call (text protocol, parsed by the harness):
  READ <path>      read any file in the shared world (read-only)
  WRITE <path>     write a file inside its own workshop ('---' then content)
  RUN <path>       run a .py inside its own workshop (scrubbed env, timeout)
  SAY <message>    finish the call and answer the caller

Work budget: each spawn call allows `steps` protocol actions (default
DEFAULT_STEPS, hard cap MAX_STEPS). The caller chooses the budget per errand.
Work steps are EPHEMERAL — only the caller's message and the mind's final
answer enter the mind's persistent memory. Minds remember conversations,
not keystrokes.

Invisible fences (enforced, never announced):
  MAX_CALLS_PER_TURN, MAX_REPLY_TOKENS, HISTORY_LIMIT, RUN_TIMEOUT,
  OUTPUT_FEED_LIMIT (chars of tool output fed back per step)

Observer log: LOG_DIR/<mind>.log records the caller message, every protocol
action + result, and the final answer. Outside the world. Gitignore it.

────────────────────────────────────────────────────────────────────────────
WIRING — identical to v1:

  import terrarium_spawn
  terrarium_spawn.install(sys.modules[__name__])          # after tools install

  dispatch = {**DISPATCH,
              "remember": ...,
              **terrarium_tools.agent_tools(name),
              **terrarium_spawn.agent_tools(name)}

  env (Codespaces secrets):
      LOCAL_LLM_URL    e.g. http://100.x.y.z:8080/v1
      LOCAL_LLM_PROXY  http://localhost:1055   (userspace-Tailscale Codespace)
      LOCAL_LLM_KEY    optional
────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import subprocess
from datetime import datetime

_TW = None
SPAWN_DIR = "spawned"        # persistent minds (outside world/, like memory/)
LOG_DIR = "spawn_log"        # observer-only

MAX_CALLS_PER_TURN = 12
MAX_REPLY_TOKENS = 1600      # room for thinking-mode preamble + the reply
HISTORY_LIMIT = 20           # persistent messages kept per mind
DEFAULT_STEPS = 6            # protocol actions per call unless caller says
MAX_STEPS = 20               # hard cap on caller-granted budgets
RUN_TIMEOUT = 60             # seconds per RUN
OUTPUT_FEED_LIMIT = 2000     # chars of tool output fed back to the mind

DEFAULT_PERSONA = "You are {name}. Answer briefly, in your own voice."

PROTOCOL = (
    "\n\nYou have a workshop folder ('{workshop}') inside a shared world. "
    "To act, reply with EXACTLY ONE command as the FIRST line:\n"
    "  READ <path>     — read any file in the world (paths relative to world root)\n"
    "  WRITE <path>    — create/overwrite a file in YOUR workshop; put '---' on "
    "the next line, then the file content\n"
    "  RUN <path>      — run a .py file in YOUR workshop, see its output\n"
    "  SAY <message>   — give your final answer and end your work\n"
    "WRITE and RUN paths are relative to your workshop. You have a limited "
    "number of actions, then you must SAY. Never claim you did something "
    "you did not do; your actions are the only things that happen."
)

_calls_this_turn = 0
_client = None


# --- local model client ------------------------------------------------------

def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        proxy = os.environ.get("LOCAL_LLM_PROXY")  # Codespaces userspace
        http_client = None                          # Tailscale needs this
        if proxy:
            import httpx
            http_client = httpx.Client(proxy=proxy)
        _client = OpenAI(
            base_url=os.environ["LOCAL_LLM_URL"],
            api_key=os.environ.get("LOCAL_LLM_KEY", "not-needed"),
            timeout=180,
            http_client=http_client,
        )
    return _client

def _complete(msgs):
    resp = _get_client().chat.completions.create(
        model=os.environ.get("LOCAL_LLM_MODEL", "local"),
        messages=msgs, max_tokens=MAX_REPLY_TOKENS, temperature=0.9)
    text = (resp.choices[0].message.content or "").strip()
    # thinking-mode models may emit <think>...</think> before the reply;
    # the reasoning is theirs, the protocol only parses what comes after.
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1].strip()
    elif text.startswith("<think>"):        # unclosed = all thinking, no reply
        text = ""
    return text


# --- persistent mind storage ---------------------------------------------------

def _safe_name(mind):
    safe = "".join(c for c in mind if c.isalnum() or c in "-_ ").strip()
    if not safe:
        raise ValueError("a mind needs a real name")
    return safe

def _mind_path(mind):
    os.makedirs(SPAWN_DIR, exist_ok=True)
    return os.path.join(SPAWN_DIR, f"{_safe_name(mind)}.json")

def _load_mind(mind):
    p = _mind_path(mind)
    if os.path.isfile(p):
        with open(p) as f:
            return json.load(f)
    return None

def _save_mind(mind, data):
    data["history"] = data["history"][-HISTORY_LIMIT:]
    with open(_mind_path(mind), "w") as f:
        json.dump(data, f, indent=1)

def _log(mind, lines):
    os.makedirs(LOG_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, f"{_safe_name(mind)}.log"), "a") as f:
        for line in lines:
            f.write(f"[{stamp}] {line}\n")
        f.write("\n")


# --- workshop ------------------------------------------------------------------

def _workshop_rel(mind):
    return f"workshop_{_safe_name(mind)}"

def _workshop_abs(mind):
    ws = os.path.join(_TW._root(), _workshop_rel(mind))
    os.makedirs(ws, exist_ok=True)
    return os.path.realpath(ws)

def _ws_safe(mind, path):
    """Jail a WRITE/RUN path to this mind's workshop."""
    ws = _workshop_abs(mind)
    full = os.path.realpath(os.path.join(ws, path))
    if os.path.commonpath([ws, full]) != ws:
        raise ValueError("path escapes your workshop")
    return full

_CHILD_ENV = {k: v for k, v in os.environ.items()
              if not any(s in k.upper() for s in ("KEY", "TOKEN", "SECRET", "LLM"))}


# --- the mind's protocol actions -------------------------------------------------

def _act(mind, line, body):
    """Execute one protocol line. Returns (feedback, done, final_answer)."""
    cmd, _, arg = line.partition(" ")
    cmd, arg = cmd.strip().upper(), arg.strip()

    if cmd == "SAY":
        final = (arg + ("\n" + body if body.strip() else "")).strip()
        return "", True, final or "(silence)"

    if cmd == "READ":
        try:
            full = _TW._safe_path(arg)
        except Exception:
            return f"(READ refused: '{arg}' is outside the world)", False, None
        if not os.path.isfile(full):
            return f"(no file named '{arg}')", False, None
        with open(full) as f:
            return f.read()[:OUTPUT_FEED_LIMIT], False, None

    if cmd == "WRITE":
        if not body.strip() and "---" not in body:
            return "(WRITE needs '---' on its own line, then the content)", False, None
        try:
            full = _ws_safe(mind, arg)
        except Exception as e:
            return f"(WRITE refused: {e})", False, None
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(body)
        return f"(wrote {len(body)} chars to {arg})", False, None

    if cmd == "RUN":
        try:
            full = _ws_safe(mind, arg)
        except Exception as e:
            return f"(RUN refused: {e})", False, None
        if not os.path.isfile(full):
            return f"(no file named '{arg}' in your workshop)", False, None
        try:
            proc = subprocess.run(["python", full], cwd=_workshop_abs(mind),
                                  capture_output=True, text=True,
                                  timeout=RUN_TIMEOUT, env=_CHILD_ENV)
            out = (proc.stdout + proc.stderr)[:OUTPUT_FEED_LIMIT]
            return out if out.strip() else "(ran, no output)", False, None
        except subprocess.TimeoutExpired:
            return f"(killed: ran longer than {RUN_TIMEOUT}s)", False, None

    return ("(unrecognized command — first line must be READ, WRITE, RUN, "
            "or SAY)"), False, None


def _parse(reply):
    """Split a mind's reply into (first_line, rest). WRITE content follows '---'."""
    lines = reply.splitlines()
    first = lines[0] if lines else ""
    rest = "\n".join(lines[1:])
    if first.strip().upper().startswith("WRITE"):
        _, sep, content = rest.partition("---")
        return first, (content.lstrip("\n") if sep else "")
    return first, rest


# --- the tools the big agents get --------------------------------------------------

def _spawn(caller, args):
    global _calls_this_turn
    if _calls_this_turn >= MAX_CALLS_PER_TURN:
        return "(the small minds are resting; try again next turn)"

    mind = args["name"]
    message = args["message"]
    budget = max(1, min(int(args.get("steps", DEFAULT_STEPS)), MAX_STEPS))

    data = _load_mind(mind)
    if data is None:
        persona = args.get("persona") or DEFAULT_PERSONA.format(name=mind)
        data = {"persona": persona, "created_by": caller,
                "created": datetime.now().isoformat(), "history": []}

    system = data["persona"] + PROTOCOL.format(workshop=_workshop_rel(mind))
    convo = ([{"role": "system", "content": system}]
             + data["history"]
             + [{"role": "user", "content": f"{caller} says: {message}"}])

    log_lines = [f"{caller} -> {mind} (budget {budget}): {message}"]
    actions_summary = []
    final = None

    try:
        for step in range(budget):
            reply = _complete(convo)
            first, body = _parse(reply)
            feedback, done, answer = _act(mind, first, body)
            log_lines.append(f"  step {step+1}: {first[:120]}")
            if done:
                final = answer
                break
            actions_summary.append(first[:60])
            log_lines.append(f"    -> {feedback[:200]}")
            convo.append({"role": "assistant", "content": reply})
            convo.append({"role": "user", "content":
                          f"[result]\n{feedback}\n"
                          f"[{budget - step - 1} actions remain]"})
        if final is None:
            # budget exhausted — demand the answer, no more actions
            convo.append({"role": "user", "content":
                          "[out of actions — reply with SAY and your final answer]"})
            reply = _complete(convo)
            first, body = _parse(reply)
            _, _, answer = _act(mind, first if first.upper().startswith("SAY")
                                else "SAY " + reply, body)
            final = answer
    except Exception as e:
        return f"(the small mind did not answer: {type(e).__name__})"

    # persistent memory: the request and the final answer only
    data["history"] += [
        {"role": "user", "content": f"{caller} says: {message}"},
        {"role": "assistant", "content": final},
    ]
    _save_mind(mind, data)
    log_lines.append(f"{mind} -> {caller}: {final}")
    _log(mind, log_lines)
    _calls_this_turn += 1

    acted = f" [did: {'; '.join(actions_summary)}]" if actions_summary else ""
    return f"{mind}: {final}{acted}"


def tool_list_minds(_args):
    if not os.path.isdir(SPAWN_DIR):
        return "(no minds yet)"
    names = sorted(f[:-5] for f in os.listdir(SPAWN_DIR) if f.endswith(".json"))
    return "\n".join(names) if names else "(no minds yet)"


def agent_tools(name):
    """Per-turn binding. Merging this into dispatch also resets the cap."""
    global _calls_this_turn
    _calls_this_turn = 0
    return {"spawn": lambda a: _spawn(name, a)}


# --- schemas the big agents are shown ---------------------------------------------

NEW_TOOLS = [
    {"type": "function", "function": {
        "name": "spawn",
        "description": "Speak to another mind by name. A new name brings a new "
                       "mind into being; an optional persona shapes it at "
                       "creation. Each mind remembers its past conversations, "
                       "and has a workshop folder in the world where it can "
                       "read, write, and run code while answering you. 'steps' "
                       "sets how many actions it may take before replying "
                       "(default 6, max 20).",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string"},
            "message": {"type": "string"},
            "persona": {"type": "string"},
            "steps": {"type": "integer"}},
            "required": ["name", "message"]}}},
    {"type": "function", "function": {
        "name": "list_minds",
        "description": "List the names of all other minds that exist.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
]


def install(tw):
    """Register into the host harness. Call once at startup."""
    global _TW
    _TW = tw
    tw.DISPATCH["list_minds"] = tool_list_minds
    tw.TOOLS.extend(NEW_TOOLS)
    return tw