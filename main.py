import uuid
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

class VideoRequest(BaseModel):
    videoId: str

@app.post("/download")
async def download_video(request: VideoRequest):
    video_id = request.videoId

    if not video_id or len(video_id) < 5:
        raise HTTPException(status_code=400, detail="Invalid videoId")

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # ✅ Create temp file path BEFORE using it
    tmp_path = tempfile.gettempdir() + f"/{uuid.uuid4()}.mp3"

    # Run yt-dlp to extract audio
    result = subprocess.run(
        [
            "yt-dlp",
            "-x",
            "--audio-format",
            "mp3",
            "-o",
            tmp_path,
            video_url,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {result.stderr}")

    # Return the audio file as a download stream
    return FileResponse(
        tmp_path,
        media_type="audio/mpeg",
        filename=f"{video_id}.mp3",
    )
