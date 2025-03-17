# mysqldb-mcp-server MCP server
[![smithery badge](https://smithery.ai/badge/@burakdirin/mysqldb-mcp-server)](https://smithery.ai/server/@burakdirin/mysqldb-mcp-server)

A MySQL database MCP server project.

## Installation

You can install the package using `uv`:

```bash
uv pip install mysqldb-mcp-server
```

Or using `pip`:

```bash
pip install mysqldb-mcp-server
```

## Components

### Tools

The server provides two tools:
- `connect_database`: Connects to a specific MySQL database
  - `database` parameter: Name of the database to connect to (string)
  - Returns a confirmation message when connection is successful

- `execute_query`: Executes MySQL queries
  - `query` parameter: SQL query/queries to execute (string)
  - Returns query results in JSON format
  - Multiple queries can be sent separated by semicolons

## Configuration

The server uses the following environment variables:

- `MYSQL_HOST`: MySQL server address (default: "localhost")
- `MYSQL_USER`: MySQL username (default: "root") 
- `MYSQL_PASSWORD`: MySQL password (default: "")
- `MYSQL_DATABASE`: Initial database (optional)
- `MYSQL_READONLY`: Read-only mode (set to 1/true to enable, default: false)

## Quickstart

### Installation

#### Claude Desktop

MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Server Configuration</summary>

```json
{
  "mcpServers": {
    "mysqldb-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/burakdirin/Projects/mysqldb-mcp-server",
        "run",
        "mysqldb-mcp-server"
      ],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "password",
        "MYSQL_DATABASE": "[optional]",
        "MYSQL_READONLY": "true"
      }
    }
  }
}
```
</details>

<details>
  <summary>Published Server Configuration</summary>

```json
{
  "mcpServers": {
    "mysqldb-mcp-server": {
      "command": "uvx",
      "args": [
        "mysqldb-mcp-server"
      ],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "password",
        "MYSQL_DATABASE": "[optional]",
        "MYSQL_READONLY": "true"
      }
    }
  }
}
```
</details>

### Installing via Smithery

To install MySQL Database Integration Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@burakdirin/mysqldb-mcp-server):

```bash
npx -y @smithery/cli install @burakdirin/mysqldb-mcp-server --client claude
```

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/burakdirin/Projects/mysqldb-mcp-server run mysqldb-mcp-server
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
