import os
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# -------------------------
# MCP Server Setup
# -------------------------
app = FastAPI(title="MCP App ID Server")

# Allow CORS for all origins (MCP Inspector browser testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MoEngage API details
MOENGAGE_URL = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"
BEARER_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEs"
    "ImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofg"
)

# -------------------------
# Models
# -------------------------
class ToolInput(BaseModel):
    db_name: str
    region: str


class CallToolRequest(BaseModel):
    name: str
    arguments: dict


# -------------------------
# MCP Endpoints
# -------------------------

@app.get("/")
def list_tools():
    """
    MCP Inspector will hit this to discover tools.
    """
    return {
        "tools": [
            {
                "name": "get-app-id",
                "description": "Fetches app ID from MoEngage API",
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


@app.post("/call")
def call_tool(req: CallToolRequest):
    """
    Handles MCP callTool for 'get-app-id'.
    """
    if req.name != "get-app-id":
        return {"error": f"Unknown tool: {req.name}"}

    payload = {
        "db_name": req.arguments.get("db_name"),
        "region": req.arguments.get("region")
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(MOENGAGE_URL, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return {"result": resp.json()}
    except requests.RequestException as e:
        return {"error": str(e)}


@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "ok"}


# -------------------------
# Start command for Render:
# uvicorn main:app --host 0.0.0.0 --port 10000
# -------------------------
