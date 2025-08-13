# app.py
# This is the main Flask application for your MCP server.
# It defines a single endpoint that fetches the app_id from the MoEngage API.

# Import necessary libraries
import os
import requests
from flask import Flask, jsonify, request

# Create a Flask web application instance
app = Flask(__name__)

# --- Configuration ---
# Set the URL for the external MoEngage API
MOENGAGE_API_URL = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"

# IMPORTANT: The token provided is for a short duration and will expire.
# You must generate a new token and update this value.
# It is best practice to store sensitive data like this in environment variables.
# For now, we'll hardcode it, but for a real deployment, use `os.environ.get('BEARER_TOKEN')`
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEsImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofh"

# --- Home Route ---
# A simple home route to confirm the server is running.
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "MCP Test Server is running!"}), 200

# --- MCP Endpoint ---
# Define a route for the MCP server endpoint.
# It handles both GET (for tool definition) and POST (for execution).
@app.route('/mcp-endpoint', methods=['GET', 'POST'])
def mcp_endpoint():
    """
    Handles the request from the MCP Inspector.
    - A GET request returns a JSON definition of the available tools.
    - A POST request executes the requested tool.
    """
    # Handle the GET request to list the available tools for the inspector.
    if request.method == 'GET':
        # This is the expected format for a tool definition for MCP.
        tool_definition = {
            "name": "fetch_app_id_tool",
            "description": "A tool that fetches the app_id from the MoEngage API.",
            "type": "function",
            "function": {
                "name": "fetch_app_id_tool",
                "description": "Fetches the MoEngage app_id for a given database name and region.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "db_name": {
                            "type": "string",
                            "description": "The name of the database, e.g., 'AbhishantC'."
                        },
                        "region": {
                            "type": "string",
                            "description": "The region code for the database, e.g., 'DC1'."
                        }
                    },
                    "required": ["db_name", "region"]
                }
            }
        }
        return jsonify([tool_definition]), 200

    # Handle the POST request to execute the tool.
    if request.method == 'POST':
        try:
            request_data = request.get_json()
            
            # This print statement is for debugging in the Render logs.
            print(f"Received JSON payload: {request_data}")

            if not request_data:
                return jsonify({"error": "No JSON payload provided"}), 400

            # The MCP inspector sends the function name and arguments in the request body.
            function_name = request_data.get("name")
            arguments = request_data.get("arguments", {})

            if function_name == "fetch_app_id_tool":
                db_name = arguments.get("db_name")
                region = arguments.get("region")

                if not db_name or not region:
                    return jsonify({"error": "Missing 'db_name' or 'region' in tool arguments"}), 400

                payload = {
                    "db_name": db_name,
                    "region": region
                }
                
                headers = {
                    "Authorization": f"Bearer {BEARER_TOKEN}",
                    "Content-Type": "application/json"
                }

                response = requests.post(MOENGAGE_API_URL, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                api_data = response.json()
                app_id = api_data.get("app_id")

                if app_id:
                    return jsonify({"app_id": app_id}), 200
                else:
                    return jsonify({"error": "App ID not found in API response"}), 500
            else:
                return jsonify({"error": f"Unknown tool: {function_name}"}), 400

        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"API request failed: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# This is a basic health check endpoint to ensure the server is running.
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200

# Run the application using Gunicorn for production.
# This part is for local testing. On Render, the `Procfile` handles this.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

