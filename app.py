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

# --- MCP Endpoint ---
# Define a route for the MCP server endpoint.
# We'll use a POST request since the external API expects a payload.
@app.route('/mcp-endpoint', methods=['POST'])
def get_app_id():
    """
    Handles the request to the MCP server. It calls the MoEngage API to
    fetch the app_id and returns it in a JSON format.
    """
    try:
        # Define the payload for the MoEngage API.
        # This can be made dynamic based on the incoming request if needed.
        payload = {
            "db_name": "AbhishantC",
            "region": "DC1"
        }
        
        # Set the headers, including the bearer token for authentication.
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }

        # Make the request to the MoEngage API.
        # Use a timeout to prevent the application from hanging.
        response = requests.post(MOENGAGE_API_URL, json=payload, headers=headers, timeout=10)
        
        # Raise an exception for bad status codes (4xx or 5xx).
        response.raise_for_status()

        # Parse the JSON response from the API.
        api_data = response.json()
        
        # Extract the app_id from the response.
        # The structure is assumed to be `{"app_id": "..."}`.
        app_id = api_data.get("app_id")

        if app_id:
            # Return a successful JSON response with the fetched app_id.
            return jsonify({"status": "success", "app_id": app_id}), 200
        else:
            # Handle cases where the app_id is not found in the API response.
            return jsonify({"status": "error", "message": "App ID not found in API response"}), 500

    except requests.exceptions.RequestException as e:
        # Handle network or HTTP errors from the MoEngage API call.
        return jsonify({"status": "error", "message": f"API request failed: {str(e)}"}), 500
    except Exception as e:
        # Handle any other unexpected errors.
        return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}), 500

# This is a basic health check endpoint to ensure the server is running.
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200

# Run the application using Gunicorn for production.
# This part is for local testing. On Render, the `Procfile` handles this.
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
