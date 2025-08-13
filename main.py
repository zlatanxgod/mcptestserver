import logging
import requests
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

app = FastAPI(title="MoEngage App ID Fetcher MCP Server")

API_URL = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEsImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofg"

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 MCP Server starting up... Ready to receive requests.")

# Root route for quick browser test
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <body>
            <h1>✅ MCP Server Running</h1>
            <p>Use MCP Inspector or POST to /call-tool</p>
        </body>
    </html>
    """

# HTTP tool listing
@app.get("/list-tools")
async def list_tools():
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

# HTTP tool call
@app.post("/call-tool")
async def call_tool(data: dict):
    if data.get("name") != "get-app-id":
        return JSONResponse({"error": "Unknown tool"}, status_code=400)

    db_name = data.get("arguments", {}).get("db_name")
    region = data.get("arguments", {}).get("region")

    if not db_name or not region:
        return JSONResponse({"error": "Missing db_name or region"}, status_code=400)

    return await fetch_app_id(db_name, region)

# Shared function
async def fetch_app_id(db_name, region):
    payload = {"db_name": db_name, "region": region}
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        logger.info(f"Calling MoEngage API with {payload}")
        resp = requests.post(API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error calling MoEngage API: {e}")
        return {"error": str(e)}

# MCP WebSocket endpoint
@app.websocket("/mcp")
async def mcp_ws(ws: WebSocket):
    await ws.accept()
    logger.info("🔌 MCP Inspector connected via WebSocket")

    while True:
        try:
            data = await ws.receive_text()
            msg = json.loads(data)
            logger.info(f"📩 Received MCP message: {msg}")

            if msg.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": {
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
                }
                await ws.send_text(json.dumps(response))

            elif msg.get("method") == "tools/call":
                params = msg.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})

                if name != "get-app-id":
                    await ws.send_text(json.dumps({
                        "jsonrpc": "2.0",
                        "id": msg.get("id"),
                        "error": {"code": -32601, "message": "Unknown tool"}
                    }))
                    continue

                result = await fetch_app_id(args.get("db_name"), args.get("region"))
                await ws.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "result": result
                }))

            else:
                await ws.send_text(json.dumps({
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "error": {"code": -32601, "message": "Unknown method"}
                }))

        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            break
