"""
terrarium_world.py — the box, now with hands.

Three DeepSeek agents share a transcript AND a single folder they can
see and change. Each agent can, on its turn:

    list_files()          see what's in the folder
    read_file(path)       open something and read it
    write_file(path,text) create or overwrite a file (incl. code)
    run_python(path)      execute a .py file and get the output back

Their whole world is ONE folder (WORLD_DIR below). The file tools refuse
to touch anything outside it. Read the SECURITY NOTE near run_python before
you run this anywhere that isn't disposable.

Run:
    pip install openai
    export DEEPSEEK_API_KEY=sk-...
    python terrarium_world.py
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
WORLD_DIR = "world"          # the agents' entire visible universe
ROUNDS = 5                   # times each agent gets a turn
MAX_TOKENS = 5000
TEMPERATURE = 1.0
MAX_TOOL_STEPS = 6           # tool calls one agent may chain in a single turn
RUN_TIMEOUT = 10             # seconds before a run_python call is killed
OUTPUT_LIMIT = 5000          # chars of tool output fed back to the agent

AGENTS = [
    {"name": "Ash", "persona": "You are skeptical and empirical. You test "
                               "claims by writing small programs and checking."},
    {"name": "Bex", "persona": "You are imaginative. You propose ideas and "
                               "leave notes and sketches in files for others."},
    {"name": "Cyr", "persona": "You are a systematizer. You organize the "
                               "folder, keep a log, and plan next steps."},
]

SEED = (
    "The three of you share one folder you can all read and write. It is your "
    "only world. You each have a name. Decide together what to build here, "
    "leave things for each other in files, and check each other's work. Begin."
)

# ---------------------------------------------------------------------------
# THE SANDBOX — every file tool routes through _safe_path, which refuses to
# resolve anywhere outside WORLD_DIR. This blocks '../' tricks and absolute
# paths for the file tools.
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
    found = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            found.append(rel)
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

def tool_run_python(args):
    # SECURITY NOTE: this executes code the AGENTS wrote. The _safe_path check
    # keeps the *file* inside the folder, but running code can do anything the
    # process can — read outside the folder, hit the network, etc. The folder
    # is NOT a security wall once this tool exists. The disposable Codespace is.
    full = _safe_path(args["path"])
    if not os.path.isfile(full):
        return f"(no file named '{args['path']}')"
    try:
        proc = subprocess.run(
            ["python", full],
            cwd=_root(),
            capture_output=True, text=True, timeout=RUN_TIMEOUT,
        )
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

TOOLS = [
    {"type": "function", "function": {
        "name": "list_files", "description": "List every file in your world folder.",
        "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a file's contents.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file", "description": "Create or overwrite a file.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"]}}},
    {"type": "function", "function": {
        "name": "run_python", "description": "Run a .py file, get its output.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
]

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

def format_transcript(transcript):
    if not transcript:
        return "(nothing said yet)"
    return "\n".join(f"{s}: {t}" for s, t in transcript)

def agent_turn(agent, transcript):
    """One agent's full turn: it may chain several tool calls, then speaks."""
    names = ", ".join(a["name"] for a in AGENTS)
    system = (
        f"{agent['persona']}\n\n"
        f"You are {agent['name']}, one of three minds ({names}) sharing a folder. "
        f"Use your tools to inspect and change the folder. When you're done "
        f"acting, say a short line to the others about what you did or think."
    )
    user = (
        f"SITUATION:\n{SEED}\n\nCONVERSATION SO FAR:\n"
        f"{format_transcript(transcript)}\n\nIt's your turn, {agent['name']}."
    )
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]

    for _ in range(MAX_TOOL_STEPS):
        resp = get_client().chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto",
            max_tokens=MAX_TOKENS, temperature=TEMPERATURE,
        )
        msg = resp.choices[0].message

        entry = {"role": "assistant", "content": msg.content or ""}
        if msg.tool_calls:
            entry["tool_calls"] = [
                {"id": tc.id, "type": "function", "function": {
                    "name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls]
        messages.append(entry)

        if not msg.tool_calls:
            return msg.content or "(said nothing)"

        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
                result = DISPATCH[name](args)
            except Exception as e:
                result = f"(tool error: {e})"
            print(f"    · {agent['name']} used {name}({tc.function.arguments})")
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": str(result)[:OUTPUT_LIMIT]})

    return "(used all tool steps without speaking)"

def run():
    print(f"\n=== Terrarium World: {len(AGENTS)} agents, {ROUNDS} rounds, "
          f"folder='{WORLD_DIR}/' ===\n")
    transcript = []
    for r in range(1, ROUNDS + 1):
        print(f"----- round {r} -----")
        for agent in AGENTS:
            try:
                line = agent_turn(agent, transcript)
            except Exception as e:
                line = f"[API error: {e}]"
            transcript.append((agent["name"], line))
            print(f"  {agent['name']}: {line}\n")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"transcript_{stamp}.txt", "w") as f:
        f.write(f"SEED: {SEED}\n\n{format_transcript(transcript)}")
    print(f"[saved transcript_{stamp}.txt — the folder '{WORLD_DIR}/' is their "
          f"persistent shared memory; inspect it to see what they built]")

if __name__ == "__main__":
    run()