import logging
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

app = FastAPI(title="MoEngage App ID Fetcher MCP Server")

API_URL = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEsImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofg"

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 MCP Server starting up... Ready to receive requests.")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    client_ip = request.client.host
    logger.info(f"Health check from {client_ip}")
    return """
    <html>
        <head><title>MCP Server</title></head>
        <body>
            <h1>✅ MoEngage MCP Server is running!</h1>
            <p>Use /list-tools and /call-tool to interact with it.</p>
        </body>
    </html>
    """

@app.get("/list-tools")
async def list_tools():
    logger.info("Tool list requested")
    return {
        "tools": [
            {
                "name": "get-app-id",
                "description": "Fetches app_id from MoEngage given db_name and region",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "db_name": {"type": "string"},
                        "region": {"type": "string"}
                    },
                    "required": ["db_name", "region"]
                }
            }
        ]
    }

@app.post("/call-tool")
async def call_tool(data: dict):
    tool_name = data.get("name")
    args = data.get("arguments", {})
    logger.info(f"Tool called: {tool_name} with args: {args}")

    if tool_name != "get-app-id":
        return JSONResponse({"error": "Unknown tool"}, status_code=400)

    db_name = args.get("db_name")
    region = args.get("region")

    if not db_name or not region:
        return JSONResponse({"error": "Missing db_name or region"}, status_code=400)

    payload = {"db_name": db_name, "region": region}
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        logger.info(f"Sending request to MoEngage API: {payload}")
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Received response: {data}")
        return {"app_id": data.get("app_id")}
    except Exception as e:
        logger.error(f"Error calling MoEngage API: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
