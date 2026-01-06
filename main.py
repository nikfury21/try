from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pytubefix import YouTube  # or pytube
import os

API_KEY = os.getenv("INTERNAL_API_KEY")

def check_key(x_api_key: str | None):
    print("API_KEY from env:", repr(API_KEY))
    print("Received x-api-key:", repr(x_api_key))
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


app = FastAPI()



@app.get("/info/{vid_id}")
async def get_info(vid_id: str, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)

    try:
        url = f"https://www.youtube.com/watch?v={vid_id}"
        yt = YouTube(url, use_po_token=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid video: {e}")

    # audio-only stream
    audio_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    # video+audio progressive stream (easiest)
    video_stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

    if not audio_stream or not video_stream:
        raise HTTPException(status_code=404, detail="No suitable streams found")

    # Option A: Direct YouTube URLs (expire quickly)
    audio_url = audio_stream.url
    video_url = video_stream.url

    return JSONResponse({
        "status": "success",
        "audio_url": audio_url,
        "video_url": video_url,
    })
