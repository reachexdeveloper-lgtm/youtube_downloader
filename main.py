from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import subprocess
import io

app = FastAPI()

class VideoRequest(BaseModel):
    videoId: str

@app.post("/download")
async def download_video(request: VideoRequest):
    video_id = request.videoId

    if not video_id or len(video_id) < 5:
        raise HTTPException(status_code=400, detail="Invalid videoId")

    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", "-",  # stdout
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return StreamingResponse(
            process.stdout,
            media_type="audio/mpeg"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")
