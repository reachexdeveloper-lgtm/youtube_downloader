from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

class VideoRequest(BaseModel):
    videoId: str

TMP_DIR = "/tmp"

@app.post("/download")
async def download_video(request: VideoRequest):
    video_id = request.videoId

    if not video_id or len(video_id) < 5:
        raise HTTPException(status_code=400, detail="Invalid videoId")

    output_file = os.path.join(TMP_DIR, f"{video_id}.mp3")

    try:
        subprocess.run([
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_file,
            f"https://www.youtube.com/watch?v={video_id}"
        ], check=True)

        if not os.path.exists(output_file):
            raise Exception("File not created")

        return {"audioPath": output_file}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")
