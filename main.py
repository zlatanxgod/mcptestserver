import requests
from fastapi.responses import HTMLResponse
from mcp.server.fastapi import FastAPI, Server
from mcp.types import Tool, ToolList, CallToolRequest, CallToolResult

# MCP Server instance
app = FastAPI()
server = Server(app, title="MoEngage App ID Fetcher MCP Server")

API_URL = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEsImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofg"

# Root route for browser check
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>MCP Server</title></head>
        <body>
            <h1>✅ MoEngage MCP Server is running!</h1>
            <p>Use MCP Inspector to connect and test the <b>get-app-id</b> tool.</p>
        </body>
    </html>
    """

# Register the MCP tool
@server.list_tools()
async def list_tools() -> ToolList:
    return ToolList(
        tools=[
            Tool(
                name="get-app-id",
                description="Fetches app_id from MoEngage given db_name and region",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "db_name": {"type": "string"},
                        "region": {"type": "string"}
                    },
                    "required": ["db_name", "region"]
                }
            )
        ]
    )

# Implement the tool's behavior
@server.call_tool()
async def call_tool(req: CallToolRequest) -> CallToolResult:
    if req.name == "get-app-id":
        db_name = req.arguments.get("db_name")
        region = req.arguments.get("region")

        payload = {"db_name": db_name, "region": region}
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return CallToolResult(content={"app_id": data.get("app_id")})
        except Exception as e:
            return CallToolResult(content={"error": str(e)})

    return CallToolResult(content={"error": "Unknown tool"})
