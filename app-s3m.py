from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello S3M Action Provider!"

@app.route('/status')
def status():
    try:
        response = requests.get("https://s3m.apps.olivine.ccs.ornl.gov/olcf/v1alpha/status", timeout=5)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502

if __name__ == '__main__':
    port = os.environ.get('FLASK_PORT') or 8080
    port = int(port)

    app.run(port=port, host='0.0.0.0')
