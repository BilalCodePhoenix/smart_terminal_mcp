"""
smart-terminal-mcp (simple + safe)

Three safety ideas, that's it:
  1. JAIL      - every path must stay inside one workspace folder (ROOT)
  2. ALLOWLIST - bash only runs a small list of harmless commands, with no shell
  3. SAFETY NET- timeouts, size limits, no overwrite by default, delete goes to trash
"""
import functools
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import shutil

from fastmcp import FastMCP

mcp = FastMCP("smart-terminal-mcp")

# ---------------------------------------------------------------- settings
ROOT = Path(os.environ.get("SMART_TERMINAL_ROOT", os.getcwd())).resolve()
TRASH = ROOT / ".trash"
TRASH.mkdir(exist_ok=True)

ALLOWED_COMMANDS = {"ls", "pwd", "echo", "git"}
GIT_READ_ONLY = {"status", "log", "diff", "show"}
SHELL_CHARS = set(";&|<>`$\n")          # used to chain/redirect commands
MAX_CHARS = 20_000                      # max output returned to the agent
MAX_FILE_BYTES = 1_000_000              # 1 MB
TIMEOUT = 20                            # seconds

# Python tools are OFF unless the person installing the server turns them on.
# Reason: Python code is NOT confined to the workspace folder.
ALLOW_PYTHON = os.environ.get("SMART_TERMINAL_ALLOW_PYTHON") == "1"
PYTHON_OFF_MESSAGE = ("Python execution is disabled. The server owner can enable it by setting "
                      "SMART_TERMINAL_ALLOW_PYTHON=1 (warning: Python code is not restricted to the workspace).")


# ---------------------------------------------------------------- helpers
def safe_path(p: str) -> Path:
    """Idea 1 (JAIL): resolve the path and refuse anything outside ROOT or sensitive."""
    path = (ROOT / p).resolve()          # also collapses ../ and follows symlinks
    if not path.is_relative_to(ROOT):
        raise ValueError("path is outside the workspace")
    for part in path.relative_to(ROOT).parts:
        if part.startswith(".env") or part in {".git", ".ssh", ".trash"} or part.endswith((".pem", ".key")):
            raise ValueError("sensitive path is blocked")
    return path


def run(argv: list) -> str:
    """Run a program WITHOUT a shell, with a timeout and a minimal environment."""
    env = {k: v for k, v in os.environ.items() if k in ("PATH", "SYSTEMROOT")}
    try:
        r = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=TIMEOUT, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return f"Timed out after {TIMEOUT}s"
    except FileNotFoundError:
        return f"'{argv[0]}' is not installed or not on PATH on this machine"
    return (r.stdout + r.stderr)[:MAX_CHARS]


def safe(tool):
    """Turn any error into a readable message instead of crashing the server."""
    @functools.wraps(tool)   # copies name, docstring AND parameter list so FastMCP can read them
    def wrapper(*args, **kwargs):
        try:
            return tool(*args, **kwargs)
        except Exception as e:
            return f"Blocked/Error: {e}"
    return wrapper


# ---------------------------------------------------------------- tools
@mcp.tool()
@safe
def bash(command: str):
    '''Run ONE allowlisted command: ls, pwd, echo, or read-only git (status/log/diff/show).
    No pipes, redirects or chaining. Use read_file / write_file / grep for file work.'''
    if SHELL_CHARS & set(command):
        raise ValueError("pipes, redirects and chaining are not allowed")
    argv = shlex.split(command)
    if not argv or argv[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"command not allowed. Allowed: {sorted(ALLOWED_COMMANDS)}")
    cmd, args = argv[0], argv[1:]

    # These three are done in pure Python, so they work the same on Windows, macOS and Linux.
    if cmd == "pwd":
        return str(ROOT)
    if cmd == "echo":
        return " ".join(args)
    if cmd == "ls":
        target = safe_path(next((a for a in args if not a.startswith("-")), "."))
        if not target.is_dir():
            raise ValueError("not a folder")
        names = []
        for p in sorted(target.iterdir()):
            try:
                safe_path(str(p))        # hide sensitive entries like .env
            except ValueError:
                continue
            names.append(p.name + ("/" if p.is_dir() else ""))
        return "\n".join(names) or "(empty folder)"

    # Only git is run as a real external program.
    if not args or args[0] not in GIT_READ_ONLY:
        raise ValueError(f"only these git commands are allowed: {sorted(GIT_READ_ONLY)}")
    if any(a.startswith(("--output", "--no-index", "-c")) for a in args):
        raise ValueError("that git flag is not allowed")
    return run(["git"] + args)


@mcp.tool()
@safe
def python_code(code: str):
    '''Run a short Python snippet (20s timeout). Disabled unless the server owner enables it.'''
    if not ALLOW_PYTHON:
        raise ValueError(PYTHON_OFF_MESSAGE)
    return run([sys.executable, "-I", "-c", code])


@mcp.tool()
@safe
def python_file(file: str):
    '''Run a .py file located inside the workspace (20s timeout). Disabled unless the server owner enables it.'''
    if not ALLOW_PYTHON:
        raise ValueError(PYTHON_OFF_MESSAGE)
    path = safe_path(file)
    if path.suffix != ".py" or not path.is_file():
        raise ValueError("must be an existing .py file")
    return run([sys.executable, str(path)])


@mcp.tool()
@safe
def glob(pattern: str):
    '''List files in the workspace matching a pattern, e.g. "**/*.py".'''
    if os.path.isabs(pattern) or ".." in Path(pattern).parts:
        raise ValueError("pattern must be relative, without '..'")
    found = []
    for m in ROOT.glob(pattern):
        try:
            safe_path(str(m))
            found.append(str(m.relative_to(ROOT)))
        except ValueError:
            continue                     # skip anything sensitive/outside
    return sorted(found)[:200]


@mcp.tool()
@safe
def grep(pattern: str, file: str):
    '''Search for text in a file inside the workspace; returns "line_number: text".'''
    path = safe_path(file)
    hits = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if pattern.lower() in line.lower():
            hits.append(f"{i}: {line}")
    return "\n".join(hits[:200]) or "No matches found."


@mcp.tool()
@safe
def read_file(file: str):
    '''Read a text file inside the workspace (max 1 MB).'''
    path = safe_path(file)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("file is too large")
    return path.read_text(encoding="utf-8", errors="replace")[:MAX_CHARS]


@mcp.tool()
@safe
def write_file(file: str, content: str, overwrite: bool = False):
    '''Write text to a file inside the workspace. Fails if the file exists unless overwrite=True.'''
    path = safe_path(file)
    if len(content.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError("content too large")
    if path.exists() and not overwrite:
        raise ValueError("file already exists - pass overwrite=True to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Content written to {file} successfully."


@mcp.tool()
@safe
def create_folder(folder: str):
    '''Create a folder inside the workspace.'''
    path = safe_path(folder)
    if path.exists():
        return f"Folder '{folder}' already exists."
    path.mkdir(parents=True)
    return f"Folder '{folder}' created successfully."


@mcp.tool()
@safe
def delete_folder(folder: str):
    '''Move a folder to .trash (soft delete, can be restored). The workspace root is protected.'''
    path = safe_path(folder)
    if path == ROOT:
        raise ValueError("cannot delete the workspace root")
    if not path.is_dir():
        return f"Folder '{folder}' does not exist."
    shutil.move(str(path), str(TRASH / f"{datetime.now():%Y%m%d_%H%M%S}_{path.name}"))
    return f"Folder '{folder}' moved to trash."


if __name__ == "__main__":
    mcp.run()