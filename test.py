import asyncio
from fastmcp import Client

config = {
    "mcpServers": {
        "smart_terminal": {
            "command": "uv",
            "args": ["run", "smart_terminal_mcp"],
        }
    }
}

async def main():
    async with Client(config) as c:
        print([t.name for t in await c.list_tools()])
        print(await c.call_tool("bash", {"command": "ls"}))
        print(await c.call_tool("bash", {"command": "ls; whoami"}))   # should be Blocked
        print(await c.call_tool("read_file", {"file": "../x.txt"}))   # should be Blocked
        print(await c.call_tool("write_file", {"file": "demo/hello.txt", "content": "hi"}))
        print(await c.call_tool("write_file", {"file": "demo/hello.txt", "content": "again"}))  # should refuse (exists)
        print(await c.call_tool("write_file", {"file": "demo/hello.txt", "content": "again", "overwrite": True}))
        print(await c.call_tool("read_file", {"file": "demo/hello.txt"}))
        print(await c.call_tool("grep", {"pattern": "again", "file": "demo/hello.txt"}))
        print(await c.call_tool("glob", {"pattern": "demo/*"}))
        print(await c.call_tool("python_code", {"code": "print(2 + 2)"}))
        print(await c.call_tool("read_file", {"file": ".env"}))          # should be Blocked
        print(await c.call_tool("delete_folder", {"folder": "demo"}))    # moves to .trash

asyncio.run(main())