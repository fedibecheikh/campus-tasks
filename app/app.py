from flask import Flask, jsonify
import os

app = Flask(__name__)
port = int(os.environ.get("PORT", "8080"))

@app.get("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
