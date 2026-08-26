import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# In Docker Compose / Kubernetes this resolves via service-name DNS
# (http://auth-service:5000). Locally in Colab we point at localhost.
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:5000")

RECORDS = [
    {"id": 1, "title": "Quarterly Report", "content": "Revenue up 12% this quarter."},
    {"id": 2, "title": "Research Notes", "content": "Experiment batch #7 results attached."},
]


def get_bearer_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header.split(" ", 1)[1]
    return None


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "data-service"})


@app.route("/data")
def data():
    token = get_bearer_token()
    if not token:
        return jsonify({"error": "missing bearer token"}), 401

    resp = requests.post(f"{AUTH_SERVICE_URL}/verify", json={"token": token}, timeout=5)
    if resp.status_code != 200:
        return jsonify({"error": "unauthorized", "detail": resp.json()}), 401

    user = resp.json()["user"]
    return jsonify({"user": user, "records": RECORDS})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, threaded=True)
