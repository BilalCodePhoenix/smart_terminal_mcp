> ⚡ Published on PyPI and compatible with MCP clients that support the stdio transport.

# Smart Terminal MCP

A lightweight **Model Context Protocol (MCP)** server built with **FastMCP** that enables AI assistants to interact with the local machine through terminal, filesystem, and Python execution tools.

The project was built to explore how MCP enables AI clients to securely communicate with external tools and automate local development workflows.

---

## ✨ Features

- Execute terminal commands
- Execute Python code snippets
- Execute Python files
- Read files
- Write files
- Search files using glob patterns
- Search text inside files
- Create folders
- Delete folders
- Lightweight and easy to extend
- Published on PyPI

---

## 🛠️ Tech Stack

- Python 3.13+
- FastMCP
- MCP
- setuptools

---

## 📦 Installation

### Using uv (Recommended)

```bash
uv add smart_terminal_mcp
```

Or run it directly without installing:

```bash
uvx smart_terminal_mcp
```

### Using pip

```bash
pip install smart_terminal_mcp
```

---


## 🚀 MCP Server Configuration

Add the following configuration to your MCP client:

```json
{
  "smart_terminal": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["smart_terminal_mcp"]
  }
}
```

Once configured, the server can be used by MCP-compatible AI clients.

---

## 📂 Available Tools

| Tool | Description |
|------|-------------|
| bash | Execute terminal commands |
| python_code | Execute Python code |
| python_file | Execute a Python file |
| read_file | Read the contents of a file |
| write_file | Create or overwrite a file |
| glob | Search files using glob patterns |
| grep | Search text inside files |
| create_folder | Create directories |
| delete_folder | Delete directories |

---

## 📁 Project Structure

```
smart_terminal_mcp/
│
├── src/
│   └── smart_terminal_mcp/
│       ├── main.py
│       ├── tools.py
│
├── pyproject.toml
├── README.md
└── LICENSE
```

---

## 🎯 Motivation

The goal of this project was to gain hands-on experience with the **Model Context Protocol (MCP)** by building a practical server that exposes useful local development tools to AI assistants.

It helped me understand:

- MCP architecture
- Tool registration
- Python packaging
- PyPI publishing
- AI tool integration
- Developer workflow automation

---

## 🔮 Roadmap

Future improvements include:

- Workspace sandboxing
- Safe command execution
- File rename and copy operations
- Git integration
- Project scaffolding
- Better error handling
- Cross-platform support
- Tool execution logging

---

## ⚠️ Disclaimer

This project is intended for educational and development purposes.

Some tools execute commands or modify files on the local machine. Only use this MCP server in trusted environments.

---

## 📜 License

MIT License

---

## 👨‍💻 Author

**Mohd Bilal**

If you found this project interesting, feel free to star the repository.