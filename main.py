import os
import subprocess
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

YT_API_KEY = os.getenv("YT_API_KEY")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = FastAPI()

def search_first_video(query: str) -> str:
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": YT_API_KEY,
        "maxResults": 1,
        "type": "video"
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if "items" not in data or not data["items"]:
        raise Exception("No video found")

    return data["items"][0]["id"]["videoId"]

def download_mp3(video_id: str) -> str:
    output = f"{DOWNLOAD_DIR}/%(title)s.%(ext)s"

    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--extractor-args", "youtube:player_client=android",
        "-o", output,
        f"https://youtu.be/{video_id}"
    ]

    subprocess.run(cmd, check=True)

    files = os.listdir(DOWNLOAD_DIR)
    if not files:
        raise Exception("Download failed")

    return os.path.join(DOWNLOAD_DIR, files[0])

@app.get("/song")
def song(q: str):
    try:
        video_id = search_first_video(q)
        mp3_path = download_mp3(video_id)

        return FileResponse(
            mp3_path,
            media_type="audio/mpeg",
            filename=os.path.basename(mp3_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
