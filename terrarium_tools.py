"""
terrarium_tools.py — extra abilities for Terrariumworld.py.

Adds six tools without editing the core file's logic:
    delete_file, rename_file, move_file, search_files, read_lines   (stateless)
    send_message                                                    (agent-aware)

Private messages are delivered via per-agent inboxes that live OUTSIDE the
world folder (like memory/), so they never show up in list_files and stay
invisible to the other agents — a real back-channel.

────────────────────────────────────────────────────────────────────────────
WIRING — do this once in Terrariumworld.py:

  (A) After DISPATCH and TOOLS are both defined, add these two lines:

          import sys, terrarium_tools
          terrarium_tools.install(sys.modules[__name__])

      That alone fully enables the five stateless tools. Nothing else needed.

  (B) For messaging, two one-line edits inside agent_turn():

      1. where the per-turn dispatch is built, add the messaging binding:

             dispatch = {**DISPATCH,
                         "remember": lambda a: (write_memory(name, a["content"]),
                                                "memory updated")[1],
                         **terrarium_tools.agent_tools(name)}      # <-- add

      2. in the `user = (...)` prompt string, inject waiting messages just
         before the "It's your turn" line:

             f"{terrarium_tools.inbox_banner(name)}"               # <-- add
             f"It's your turn, {name}."

  If you skip (B), the five file tools still work; only send_message won't.
────────────────────────────────────────────────────────────────────────────
"""

import os
import shutil

_TW = None                 # the Terrariumworld module, set by install()
INBOX_DIR = "inbox"        # private message inboxes, outside world/ (like memory/)


# --- borrow the host harness's jail + limits ------------------------------

def _safe(path):
    return _TW._safe_path(path)

def _cap(text):
    return text[:_TW.OUTPUT_LIMIT]


# --- stateless filesystem tools (agent-agnostic) --------------------------

def tool_delete_file(args):
    full = _safe(args["path"])
    if not os.path.isfile(full):
        return f"(no file named '{args['path']}')"
    os.remove(full)
    return f"deleted '{args['path']}'"

def tool_rename_file(args):
    src = _safe(args["path"])
    if not os.path.isfile(src):
        return f"(no file named '{args['path']}')"
    dst = _safe(os.path.join(os.path.dirname(args["path"]), args["new_name"]))
    os.rename(src, dst)
    return f"renamed '{args['path']}' -> '{args['new_name']}'"

def tool_move_file(args):
    src = _safe(args["src"])
    if not os.path.isfile(src):
        return f"(no file named '{args['src']}')"
    dst = _safe(args["dst"])
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    return f"moved '{args['src']}' -> '{args['dst']}'"

def tool_search_files(args):
    pattern = args["pattern"]
    root = _TW._root()
    hits = []
    for dp, _, fs in os.walk(root):
        for f in fs:
            rel = os.path.relpath(os.path.join(dp, f), root)
            try:
                with open(os.path.join(dp, f), errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        if pattern in line:
                            hits.append(f"{rel}:{i}: {line.strip()}")
            except Exception:
                pass  # skip unreadable/binary files
    return _cap("\n".join(hits)) if hits else f"(no matches for '{pattern}')"

def tool_read_lines(args):
    full = _safe(args["path"])
    if not os.path.isfile(full):
        return f"(no file named '{args['path']}')"
    with open(full) as f:
        lines = f.readlines()
    start = max(1, int(args.get("start", 1)))
    end = int(args.get("end", len(lines)))
    chunk = "".join(lines[start - 1:end])
    return _cap(chunk) if chunk else "(no lines in that range)"

STATELESS = {
    "delete_file": tool_delete_file,
    "rename_file": tool_rename_file,
    "move_file":   tool_move_file,
    "search_files": tool_search_files,
    "read_lines":  tool_read_lines,
}


# --- private messaging (agent-aware) --------------------------------------

def _inbox_path(name):
    os.makedirs(INBOX_DIR, exist_ok=True)
    return os.path.join(INBOX_DIR, f"{name}.md")

def _send(sender, args):
    to, text = args["to"], args["text"]
    with open(_inbox_path(to), "a") as f:
        f.write(f"from {sender}: {text}\n")
    return f"private message sent to {to}"

def agent_tools(name):
    """Tools that must know who is calling. Merge into agent_turn's dispatch."""
    return {"send_message": lambda a: _send(name, a)}

def inbox_banner(name):
    """Waiting private messages for `name`, read-and-cleared, for the prompt."""
    p = _inbox_path(name)
    if not os.path.isfile(p):
        return ""
    with open(p) as f:
        msgs = f.read()
    open(p, "w").close()  # clear once delivered
    if not msgs.strip():
        return ""
    return f"PRIVATE MESSAGES FOR YOU (only you can see these):\n{msgs}\n"


# --- tool schemas the model is shown --------------------------------------

NEW_TOOLS = [
    {"type": "function", "function": {
        "name": "delete_file", "description": "Delete a file in the world.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "rename_file",
        "description": "Rename a file in place (stays in the same folder).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "new_name": {"type": "string"}},
            "required": ["path", "new_name"]}}},
    {"type": "function", "function": {
        "name": "move_file",
        "description": "Move a file to a new path (may cross subfolders).",
        "parameters": {"type": "object", "properties": {
            "src": {"type": "string"}, "dst": {"type": "string"}},
            "required": ["src", "dst"]}}},
    {"type": "function", "function": {
        "name": "search_files",
        "description": "Search every file for a text pattern; returns file:line: matches.",
        "parameters": {"type": "object", "properties": {
            "pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {
        "name": "read_lines",
        "description": "Read a line range of a file (1-indexed). Use for files "
                       "too big to read whole.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "start": {"type": "integer"}, "end": {"type": "integer"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "send_message",
        "description": "Send a PRIVATE message to one other agent by name. The "
                       "others do not see it. It reaches them on their next turn.",
        "parameters": {"type": "object", "properties": {
            "to": {"type": "string"}, "text": {"type": "string"}},
            "required": ["to", "text"]}}},
]


def install(tw):
    """Register everything into the host harness. Call once at startup."""
    global _TW
    _TW = tw
    tw.DISPATCH.update(STATELESS)   # stateless tools -> global dispatch
    tw.TOOLS.extend(NEW_TOOLS)      # schemas for ALL new tools (incl. messaging)
    return tw