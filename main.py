from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import subprocess
import tempfile
import os

app = FastAPI()

COOKIES_PATH = "./cookies.txt"  
class VideoRequest(BaseModel):
    videoId: str

@app.post("/download")
async def download_video(request: VideoRequest):
    video_id = request.videoId

    if not video_id or len(video_id) < 5:
        raise HTTPException(status_code=400, detail="Invalid videoId")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    cmd = [
        "yt-dlp",
        f"https://www.youtube.com/watch?v={video_id}",
        "--extract-audio",
        "--audio-format", "mp3",
        "-f", "bestaudio",
        "--cookies", COOKIES_PATH,
        "-o", tmp_path,  # save to temp file
        "--no-progress",  # optional: cleaner logs
        "--quiet"         # optional: suppress verbose output
    ]

    try:
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            err_msg = result.stderr.decode()
            # Handle common errors
            if "Sign in to confirm" in err_msg:
                raise HTTPException(403, detail="YouTube requires login. Check cookies.")
            raise HTTPException(500, detail=f"yt-dlp failed: {err_msg}")

        # Stream the temporary file
        def iterfile():
            with open(tmp_path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk
            os.remove(tmp_path)

        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")
