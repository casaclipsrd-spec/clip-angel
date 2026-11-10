from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse

app = FastAPI(title="Clip Angel")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/")
def home():
    return {
        "message": "Clip Angel está funcionando",
        "status": "online"
    }

@app.post("/analyze")
def analyze(data: VideoRequest):
    url = data.url.strip()
    parsed = urlparse(url)

    if parsed.hostname not in [
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
        "m.youtube.com"
    ]:
        return {"error": "Introduce un enlace válido de YouTube"}

    return {
        "status": "received",
        "message": "Enlace recibido correctamente",
        "url": url
    }
from fastapi import UploadFile, File
import os
import shutil

os.makedirs("videos", exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    filename = os.path.basename(file.filename)

    if not filename.lower().endswith((".mp4", ".mov", ".mkv")):
        return {"error": "Formato no compatible"}

    path = os.path.join("videos", filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Video recibido correctamente",
        "filename": filename
    }
