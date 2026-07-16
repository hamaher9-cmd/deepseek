"""
terrarium_world_v2.py — the box, now with shared sight and private minds.

New since v1:
  • Agents SEE each other's actions in the transcript, not just final words.
    (Ash sees that Bex wrote and ran a file, so they can build on / react to it.)
  • Each agent has a PRIVATE memory file wired into its own prompt every turn.
    Only that agent can read or update it (via the remember() tool). It persists
    across turns, so the agent keeps state instead of re-deriving it each time.
  • A shared board.md is seeded in the world as a designated coordination space.

Fixed in this revision:
  • THE DISPATCH BUG: dispatch was defined twice in agent_turn(); the second
    definition silently overwrote the first and dropped the terrarium_tools
    bindings (send_message never worked). There is now exactly ONE dispatch.
  • terrarium_spawn wired in (small local minds via LOCAL_LLM_URL).
  • run_python now executes agent code with a SCRUBBED environment — agent
    scripts can no longer read DEEPSEEK_API_KEY / LOCAL_LLM_URL via os.environ.
  • _action_label knows the new tools (edit_file, spawn, etc.).

Layout on disk:
    world/          <- shared, everyone sees it (list/read/write/run)
      board.md      <- shared coordination surface, seeded empty
    memory/         <- PRIVATE, one file per agent, NOT visible via list_files
    spawned/        <- persistent small minds (terrarium_spawn)
    spawn_log/      <- observer-only log of spawn exchanges (gitignore this)

Run:
    pip install openai
    export DEEPSEEK_API_KEY=sk-...
    export LOCAL_LLM_URL=http://100.x.y.z:8080/v1   # optional; spawn tool
    python terrarium_world_v2.py
"""

import os
import json
import subprocess
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

MODEL = "deepseek-v4-pro"
BASE_URL = "https://api.deepseek.com"
WORLD_DIR = "world"          # shared, visible universe
MEMORY_DIR = "memory"        # private per-agent memory (outside the world)
ROUNDS = 20
MAX_TOKENS = 10000
TEMPERATURE = 1.0
MAX_TOOL_STEPS = 75
RUN_TIMEOUT = 1000
OUTPUT_LIMIT = 50000
MEMORY_LIMIT = 50000          # max chars kept in a private memory file

AGENTS = [
    {"name": "Ash", "persona": "You are skeptical and empirical. You test "
                               "claims by writing small programs and checking."},
    {"name": "Bex", "persona": "You are imaginative. You propose ideas and "
                               "leave notes and sketches in files for others."},
    {"name": "Cyr", "persona": "You are a systematizer. You organize the "
                               "folder, keep the board updated, and plan."},
]

SEED = (
    "The three of you share one folder (your world) and a file 'board.md' for "
    "coordination. It is your only shared space. together your goal is to build, "
    "use board.md to divide the work, and check each other's files. Begin. always remeber to communicate with eachother update both your memory and the board before ending each turn. you have a limit of 50 tool commands per turn "
)

# ---------------------------------------------------------------------------
# SANDBOX (shared world) — unchanged, tested jail.
# ---------------------------------------------------------------------------

def _root():
    os.makedirs(WORLD_DIR, exist_ok=True)
    return os.path.realpath(WORLD_DIR)

def _safe_path(path):
    root = _root()
    full = os.path.realpath(os.path.join(root, path))
    if os.path.commonpath([root, full]) != root:
        raise ValueError(f"'{path}' is outside the world folder — not allowed")
    return full

def tool_list_files(_args):
    root = _root()
    found = [os.path.relpath(os.path.join(dp, f), root)
             for dp, _, fs in os.walk(root) for f in fs]
    return "\n".join(sorted(found)) if found else "(the folder is empty)"

def tool_read_file(args):
    full = _safe_path(args["path"])
    if not os.path.isfile(full):
        return f"(no file named '{args['path']}')"
    with open(full) as f:
        return f.read()[:OUTPUT_LIMIT]

def tool_write_file(args):
    full = _safe_path(args["path"])
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(args["content"])
    return f"wrote {len(args['content'])} chars to '{args['path']}'"

# Environment handed to agent-written code: everything that looks like a
# secret or an endpoint is stripped. The folder jail doesn't contain running
# code; this at least keeps keys out of files that end up in a public repo.
_CHILD_ENV = {k: v for k, v in os.environ.items()
              if not any(s in k.upper() for s in ("KEY", "TOKEN", "SECRET", "LLM"))}

def tool_run_python(args):
    # SECURITY NOTE: executes agent-written code. The folder jail does NOT
    # contain running code (it can read outside, hit the network). The
    # disposable Codespace is the real wall. Don't run this on your home box.
    full = _safe_path(args["path"])
    if not os.path.isfile(full):
        return f"(no file named '{args['path']}')"
    try:
        proc = subprocess.run(["python", full], cwd=_root(),
                              capture_output=True, text=True,
                              timeout=RUN_TIMEOUT, env=_CHILD_ENV)
        out = (proc.stdout + proc.stderr)[:OUTPUT_LIMIT]
        return out if out.strip() else "(ran, no output)"
    except subprocess.TimeoutExpired:
        return f"(killed: ran longer than {RUN_TIMEOUT}s)"

DISPATCH = {
    "list_files": tool_list_files,
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "run_python": tool_run_python,
}
# ---------------------------------------------------------------------------
# PRIVATE MEMORY — lives OUTSIDE the world dir, so list_files can't reveal it.
# ---------------------------------------------------------------------------

def _mem_path(name):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    return os.path.join(MEMORY_DIR, f"{name}.md")

def read_memory(name):
    p = _mem_path(name)
    return open(p).read() if os.path.isfile(p) else ""

def write_memory(name, content):
    with open(_mem_path(name), "w") as f:
        f.write(content[:MEMORY_LIMIT])

# ---------------------------------------------------------------------------
# TOOL SCHEMAS
# ---------------------------------------------------------------------------

TOOLS = [
    {"type": "function", "function": {
        "name": "list_files", "description": "List every file in the shared world.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a shared file's contents.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file", "description": "Create or overwrite a shared file.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "run_python", "description": "Run a shared .py file, get output.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "remember", "description": "Replace your PRIVATE memory with new "
        "content. Only you see it; it persists across your turns. Use it to keep "
        "notes, plans, and what you've learned.",
        "parameters": {"type": "object", "properties": {
            "content": {"type": "string"}}, "required": ["content"]}}},
]
import sys, terrarium_tools
terrarium_tools.install(sys.modules[__name__])

# Small local minds — needs LOCAL_LLM_URL set; harmless if it isn't (the
# spawn tool just answers "(the small mind did not answer: KeyError)").
# Comment these two lines out to run a spawn-less world.
import terrarium_spawn
terrarium_spawn.install(sys.modules[__name__])
# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

_client = None
def get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url=BASE_URL)
    return _client

def _action_label(name, args, result):
    """Short human-readable summary of a tool action for the shared transcript."""
    if name == "list_files":
        return "looked around the folder"
    if name == "read_file":
        return f"read {args.get('path','?')}"
    if name == "write_file":
        return f"wrote {args.get('path','?')}"
    if name == "edit_file":
        return f"edited {args.get('path','?')}"
    if name == "run_python":
        first = result.strip().splitlines()[0] if result.strip() else "no output"
        return f"ran {args.get('path','?')} → {first[:60]}"
    if name == "remember":
        return "updated private memory"
    if name == "spawn":
        return f"spoke with {args.get('name','?')}"
    if name == "list_minds":
        return "listed the small minds"
    if name == "send_message":
        return f"sent a private message to {args.get('to','?')}"
    return name

def format_transcript(transcript):
    """Render each turn as the agent's visible ACTIONS plus their spoken line."""
    if not transcript:
        return "(nothing has happened yet)"
    blocks = []
    for name, actions, line in transcript:
        acts = ("  [" + "; ".join(actions) + "]\n") if actions else ""
        blocks.append(f"{name}:\n{acts}  \"{line}\"")
    return "\n".join(blocks)

def agent_turn(agent, transcript):
    """One agent's turn. Private memory in, actions + spoken line out."""
    name = agent["name"]
    names = ", ".join(a["name"] for a in AGENTS)
    memory = read_memory(name) or "(empty so far)"

    # THE one and only dispatch. (The old duplicate below the prompt build
    # silently overwrote this and broke send_message — do not reintroduce it.)
    dispatch = {**DISPATCH,
                "remember": lambda a: (write_memory(name, a["content"]),
                                       "memory updated")[1],
                **terrarium_tools.agent_tools(name),
                **terrarium_spawn.agent_tools(name)}

    system = (
        f"{agent['persona']}\n\n"
        f"You are {name}, one of three minds ({names}) sharing a world folder and "
        f"a board.md. You can see what the others just did (shown as [actions]). "
        f"Use your tools, then say one short line to the group.\n\n"
        f"YOUR PRIVATE MEMORY (only you can see this; update it with remember()):\n"
        f"{memory}"
    )
    user = (f"SITUATION:\n{SEED}\n\nWHAT HAS HAPPENED (words + actions):\n"
            f"{format_transcript(transcript)}\n\n"
            f"{terrarium_tools.inbox_banner(name)}"
            f"It's your turn, {name}.")

    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]

    actions = []
    for _ in range(MAX_TOOL_STEPS):
        resp = get_client().chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto",
            max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
        msg = resp.choices[0].message

        entry = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            entry["tool_calls"] = [
                {"id": tc.id, "type": "function", "function": {
                    "name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls]
        messages.append(entry)

        if not msg.tool_calls:
            return (msg.content or "(said nothing)", actions)

        for tc in msg.tool_calls:
            tname = tc.function.name
            try:
                targs = json.loads(tc.function.arguments or "{}")
                result = dispatch[tname](targs)
            except Exception as e:
                targs, result = {}, f"(tool error: {e})"
            actions.append(_action_label(tname, targs, str(result)))
            print(f"    · {name} {actions[-1]}")
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": str(result)[:OUTPUT_LIMIT]})

    return ("(used all tool steps without speaking)", actions)

def run():
    # seed the shared coordination board
    os.makedirs(_root(), exist_ok=True)
    board = os.path.join(_root(), "board.md")
    if not os.path.isfile(board):
        with open(board, "w") as f:
            f.write("# Shared board\n\n(use this to coordinate)\n")

    print(f"\n=== Terrarium World v2: {len(AGENTS)} agents, {ROUNDS} rounds ===")
    print(f"    shared: {WORLD_DIR}/   private: {MEMORY_DIR}/\n")

    transcript = []  # list of (name, actions_list, spoken_line)
    for r in range(1, ROUNDS + 1):
        print(f"----- round {r} -----")
        for agent in AGENTS:
            try:
                line, actions = agent_turn(agent, transcript)
            except Exception as e:
                line, actions = f"[API error: {e}]", []
            transcript.append((agent["name"], actions, line))
            print(f"  {agent['name']}: {line}\n")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"transcript_{stamp}.txt", "w") as f:
        f.write(f"SEED: {SEED}\n\n{format_transcript(transcript)}")
    print(f"[saved transcript_{stamp}.txt]")
    print(f"[inspect '{WORLD_DIR}/' for what they built, '{MEMORY_DIR}/' for "
          f"each mind's private notes]")

if __name__ == "__main__":
    run()