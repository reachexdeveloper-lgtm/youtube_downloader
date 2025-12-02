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

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = tmp.name
    tmp.close()

    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", "-",  # stdout
        f"https://www.youtube.com/watch?v={video_id}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            raise HTTPException(500, result.stderr.decode())

        def iterfile():
            with open(tmp_path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk
            os.remove(tmp_path)

        return StreamingResponse(iterfile(), media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"yt-dlp error: {str(e)}")
