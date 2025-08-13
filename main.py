from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

API_URL = "https://intercom-api-gateway.moengage.com/v2/iw/fetch-appid"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJpbnRlcmNvbSIsImNoYW5uZWwiOiJhcGkiLCJpYXQiOjE3NTQ5OTY5ODEsImV4cCI6MTc1NTA4MzM4MX0.xxpnkQ4vmzPZKhGNkZ2JvllyOZY--kNLP2MBW5v6ofg"

@app.post("/get-app-id")
def get_app_id(db_name: str, region: str):
    payload = {
        "db_name": db_name,
        "region": region
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return {"app_id": data.get("app_id")}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
