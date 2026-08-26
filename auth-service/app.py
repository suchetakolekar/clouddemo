import datetime
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# Demo-only secret. In real deployments this comes from an env var or a
# Kubernetes Secret / Vault — never hardcoded.
SECRET_KEY = "demo-secret-key-change-in-production"

USERS = {
    "alice": "wonderland123",
    "bob": "builder456",
}


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "auth-service"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) != password:
        return jsonify({"error": "invalid credentials"}), 401

    now = datetime.datetime.utcnow()
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=30),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return jsonify({"access_token": token, "token_type": "bearer"})


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(force=True) or {}
    token = data.get("token", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"valid": True, "user": payload["sub"]})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "invalid token"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
