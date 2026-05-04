# utility-mcp-server

A lightweight MCP (Model Context Protocol) server built with Python and FastMCP that exposes three utility tools over stdio transport.

mcp-name: io.github.prakhargour10/utility-mcp-server

## Tools

| Tool | Description |
|---|---|
| `get_current_time()` | Returns the current time in IST (Indian Standard Time) |
| `get_current_date()` | Returns the current date in IST (Indian Standard Time) |
| `get_share_price(company_name)` | Returns the latest share price of a company by name (e.g. "Infosys", "Apple") |

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`

## Installation

```bash
git clone https://github.com/prakhargour10/utility-mcp-server.git
cd utility-mcp-server
pip install -r requirements.txt
```

## Usage

### Run directly

```bash
python main.py
```

### Add to VS Code (Copilot Agent mode)

Add to your VS Code `settings.json`:

```json
"mcp": {
  "servers": {
    "utility": {
      "type": "stdio",
      "command": "python",
      "args": ["path/to/utility-mcp-server/main.py"]
    }
  }
}
```

### Add to Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "utility": {
      "command": "python",
      "args": ["path/to/utility-mcp-server/main.py"]
    }
  }
}
```

## License

MIT
