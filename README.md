> ⚡ Published on PyPI and compatible with MCP clients that support the stdio transport.

# Smart Terminal MCP

A lightweight **Model Context Protocol (MCP)** server built with **FastMCP** that lets AI assistants work with files, git and Python on your local machine, **inside a protected workspace folder**.

Giving an AI agent a raw terminal is risky: it could delete files, read secrets or run commands you never intended. This project explores how to expose useful local tools to MCP clients **with safety nets built in**.

---

## ✨ Features

- List, read, write and search files (`glob`, `grep`, `read_file`, `write_file`)
- Create and (softly) delete folders
- Run a small allowlist of safe commands: `ls`, `pwd`, `echo` and **read-only git** (`status`, `log`, `diff`, `show`)
- Run Python code and Python files (**opt-in**, off by default)
- Every file operation is confined to one workspace folder
- Works on Windows, macOS and Linux (developed and tested on Windows)
- One command to run: `uvx smart_terminal_mcp`

---

## 🛡️ Security Model

| Safety net | What it does |
|------------|--------------|
| **Workspace jail** | Every path is resolved to its real location (`../` and symlinks included) and must stay inside the workspace folder |
| **Secrets blocklist** | `.env*`, `.git`, `.ssh`, `*.pem`, `*.key` and `.trash` cannot be read, written or listed |
| **No raw shell** | `bash` never uses a shell. It runs only allowlisted commands, and `;` `&` `\|` `>` `<` `` ` `` `$` are rejected |
| **Read-only git** | Only `status`, `log`, `diff`, `show`; risky flags like `--output` and `--no-index` are blocked |
| **Limits** | 20 s timeout, 20,000-character output cap, 1 MB file-size cap |
| **Clean environment** | Launched programs only receive `PATH` and `SYSTEMROOT`, so your API keys are not exposed to them |
| **No accidental overwrite** | `write_file` refuses to replace an existing file unless `overwrite=True` |
| **Soft delete** | `delete_folder` moves folders to `.trash/` instead of destroying them; the workspace root can never be deleted |
| **Friendly errors** | Anything blocked returns a readable `Blocked/Error: ...` message so the agent can adjust |
| **Python is opt-in** | `python_code` / `python_file` are disabled unless you set `SMART_TERMINAL_ALLOW_PYTHON=1` |

### ⚠️ Important limitation

The folder jail protects the **file, search and git tools**. **Python execution is not sandboxed**: when enabled, Python code can access anything your user account can. Enable it only with agents you trust, or run the server inside Docker (on the roadmap).

---

## 📦 Installation

### Using uv (Recommended)

Run it directly without installing:

```bash
uvx smart_terminal_mcp
```

Or add it to a project:

```bash
uv add smart_terminal_mcp
```

### Using pip

```bash
pip install smart_terminal_mcp
```

---

## 🚀 MCP Server Configuration

You need an MCP client (Claude Desktop, Claude Code, Cursor, VS Code, Codex, or your own LangGraph app) and [`uv`](https://docs.astral.sh/uv/) installed.

### Claude Desktop / Cursor style

```json
{
  "mcpServers": {
    "smart_terminal": {
      "command": "uvx",
      "args": ["smart_terminal_mcp"],
      "env": {
        "SMART_TERMINAL_ROOT": "C:\\Users\\me\\projects\\my-app"
      }
    }
  }
}
```

### LangChain MCP adapters style

```json
{
  "smart_terminal": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["smart_terminal_mcp"],
    "env": {
      "SMART_TERMINAL_ROOT": "/path/to/workspace"
    }
  }
}
```

### Claude Code

```bash
claude mcp add smart_terminal -- uvx smart_terminal_mcp
```

### Settings (environment variables)

| Variable | Default | Meaning |
|----------|---------|---------|
| `SMART_TERMINAL_ROOT` | current folder | The workspace folder every tool is confined to. **Set this explicitly.** |
| `SMART_TERMINAL_ALLOW_PYTHON` | off | Set to `1` to enable `python_code` and `python_file` |

---

## 📂 Available Tools

| Tool | Description |
|------|-------------|
| `bash` | Run one allowlisted command: `ls`, `pwd`, `echo`, or read-only `git` |
| `python_code` | Run a Python snippet (opt-in, 20 s timeout) |
| `python_file` | Run a `.py` file from the workspace (opt-in, 20 s timeout) |
| `read_file` | Read a text file in the workspace (max 1 MB) |
| `write_file` | Create a file; overwrites only with `overwrite=True` |
| `glob` | List files matching a pattern such as `**/*.py` |
| `grep` | Search for text inside a file |
| `create_folder` | Create a folder in the workspace |
| `delete_folder` | Move a folder to `.trash/` (recoverable) |

---

## 🔄 How It Works

```
LLM  ⇄  MCP client (Claude, Cursor, ...)  ⇄  smart_terminal_mcp  ⇄  workspace folder
 (cloud)        (on your computer)        (started by uvx, stdio)     (your files and git)
```

1. Your MCP client starts the server with `uvx smart_terminal_mcp`.
2. The LLM asks the client to call a tool; the client forwards it over stdio.
3. The server validates the request (path jail, allowlist, limits) and only then runs it.
4. The result, or a `Blocked/Error` message, goes back to the LLM.

The server runs entirely on your own machine. Nothing is hosted.

---

## 🧪 Testing

```bash
uv run python test.py
```

Or open the MCP Inspector against the server:

```bash
npx @modelcontextprotocol/inspector uv run smart_terminal_mcp
```

Things worth trying: `ls; whoami` (blocked), reading `../anything` (blocked), reading `.env` (blocked), writing to an existing file without `overwrite=True` (refused).

---

## 📁 Project Structure

```
smart_terminal_mcp/
│
├── src/
│   └── smart_terminal_mcp/
│       ├── main.py
│       └── tools.py
│
├── test.py
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 🎯 Motivation

The goal of this project was to gain hands-on experience with the **Model Context Protocol (MCP)** by building a practical server, and to learn why **safety design matters** when AI agents can touch a real machine.

It helped me understand:

- MCP architecture and the stdio transport
- Tool registration with FastMCP
- Path traversal and why paths must be resolved before checking
- Why raw `shell=True` is dangerous, and allowlisting as an alternative
- Python packaging and PyPI publishing
- Honest threat modelling: what a safeguard does and does not protect

---

## 🔮 Roadmap

- Docker mode for a true sandbox (including Python execution)
- `delete_file`, `edit_file` (partial edits), `move` and `copy` operations
- More read-only commands and richer `ls` options
- Git actions with explicit approval (add, commit)
- Tool execution audit log
- More testing on macOS and Linux

---

## ⚠️ Disclaimer

This project is intended for educational and development purposes. Even with the safety nets above, only connect it to agents and clients you trust, and point `SMART_TERMINAL_ROOT` at a dedicated project folder, never at your home directory or system folders.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Mohd Bilal**

If you found this project interesting, feel free to star the repository.