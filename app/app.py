from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)
port = int(os.environ.get("PORT", "8080"))

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/db-check")
def db_check():
    host = os.environ.get("DB_HOST", "db")
    db_port = int(os.environ.get("DB_PORT", "5432"))
    try:
        with socket.create_connection((host, db_port), timeout=3):
            return jsonify(db=f"{host}:{db_port}", reachable=True)
    except OSError as e:
        return jsonify(db=f"{host}:{db_port}", reachable=False, erreur=str(e)), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
