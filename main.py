from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pytubefix import YouTube
import os

API_KEY = os.getenv("INTERNAL_API_KEY")
TOKEN_FILE = "/tmp/tokens.json"  # Writable; pre-populate via repo or build script

def check_key(x_api_key: str | None):
    print("Received x-api-key:", repr(x_api_key))
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

app = FastAPI()

@app.get("/info/{vid_id}")
async def get_info(vid_id: str, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    url = f"https://www.youtube.com/watch?v={vid_id}"
    try:
        yt = YouTube(
            url,
            client="WEB",
            use_po_token=True,
            token_file=TOKEN_FILE
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid video: {str(e)}")

    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    video_stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

    if not audio_stream:
        raise HTTPException(status_code=404, detail="No audio stream found")
    if not video_stream:
        raise HTTPException(status_code=404, detail="No video stream found")

    return JSONResponse({
        "status": "success",
        "audio_url": audio_stream.url,
        "video_url": video_stream.url,
        "title": yt.title or "Unknown",
        "duration": yt.length
    })
