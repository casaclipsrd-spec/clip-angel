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
import subprocess

os.makedirs("clips", exist_ok=True)

class ClipRequest(BaseModel):
    filename: str

@app.post("/create-clips")
def create_clips(data: ClipRequest):
    filename = os.path.basename(data.filename)
    video_path = os.path.join("videos", filename)

    if not os.path.exists(video_path):
        return {"error": "No se encontró el video"}

    os.makedirs("clips", exist_ok=True)

    output_pattern = os.path.join(
        "clips",
        os.path.splitext(filename)[0] + "_%03d.mp4"
    )

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf",
        "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
        "-c:v", "libx264",
"-threads", "2",
        "-preset", "ultrafast",
        "-crf", "28",
        "-c:a", "aac",
        "-b:a", "96k",
        "-f", "segment",
        "-segment_time", "45",
        "-reset_timestamps", "1",
        output_pattern
    ]

    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=120
        )
    except subprocess.TimeoutExpired:
        return {"error": "El procesamiento tardó demasiado"}

    if resultado.returncode != 0:
        return {
            "error": "No se pudieron crear los clips",
            "detalle": resultado.stderr[-1500:]
        }

    clips_creados = [
        nombre for nombre in os.listdir("clips")
        if nombre.startswith(os.path.splitext(filename)[0] + "_")
        and nombre.endswith(".mp4")
    ]

    return {
        "message": "Clips creados correctamente",
        "clips": clips_creados
    }
from fastapi.responses import FileResponse

@app.get("/download/{filename}")
def download_clip(filename: str):
    filename = os.path.basename(filename)
    path = os.path.join("clips", filename)

    if not os.path.exists(path):
        return {"error": "Clip no encontrado"}

    return FileResponse(
        path,
        media_type="video/mp4",
        filename=filename
    )
@app.get("/clips")
def listar_clips():
    os.makedirs("clips", exist_ok=True)

    archivos = [
        nombre for nombre in os.listdir("clips")
        if nombre.endswith(".mp4")
    ]

    return {
        "clips": archivos
    }
