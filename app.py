from flask import Flask, redirect, render_template, jsonify, request
from yt import get_streams
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
COOKIE_PATH = os.getenv("COOKIE_PATH")

def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get("x-api-key")  # Clients send key in header
        if key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Needed to avoid Flask route errors
    return wrapper

@app.route("/")
def home():
    return "Hello, Welcome to the Code World Youtube Downloader API"


@app.route("/get/video/streams", methods=["post"])
@require_api_key
def get_video_streams():
    video_url = request.json.get("video_url")
    try:
        title, audios, muxed, videos = get_streams(video_url)
        return jsonify({"title": title, "audios": audios, "videos": videos})
    except Exception as e:
        return jsonify({"error": e})
    

if __name__ == "__main__":
    app.debug = True
    app.run()