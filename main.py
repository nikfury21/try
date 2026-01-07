from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
import yt_dlp
import os

API_KEY = os.getenv("INTERNAL_API_KEY")

def check_key(x_api_key: str | None):
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

app = FastAPI()

@app.get("/info/{vid_id}")
async def get_info(vid_id: str, x_api_key: str | None = Header(default=None)):
    check_key(x_api_key)
    url = f"https://www.youtube.com/watch?v={vid_id}"
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'cookiefile': os.path.join(os.path.dirname(__file__), 'cookies.txt')
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            video_formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
            
            audio_url = audio_formats[0]['url'] if audio_formats else None
            video_url = video_formats[0]['url'] if video_formats else None
            
            if not audio_url:
                raise HTTPException(status_code=404, detail="No audio stream found")
        
        return JSONResponse({
            "status": "success",
            "audio_url": audio_url,
            "video_url": video_url,
            "title": info.get('title', 'Unknown'),
            "duration": info.get('duration', 0)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Video error: {str(e)}")
