from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from app.audio_processing import process_audio_file

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

@app.post("/upload/")
async def upload_audio(
    file: UploadFile = File(...),
    slow_pct: float = Form(...),
    reverb_pct: float = Form(...)
):
    filename = os.path.join(UPLOAD_DIR, file.filename)
    with open(filename, "wb") as f:
        f.write(await file.read())

    output_path = os.path.join(PROCESSED_DIR, f"processed_{file.filename.replace('.mp3', '.wav')}")
    process_audio_file(filename, output_path, slow_pct, reverb_pct)

    return {"download_url": f"/download/{os.path.basename(output_path)}"}

@app.get("/download/{filename}")
def download_file(filename: str):
    return FileResponse(os.path.join(PROCESSED_DIR, filename), media_type="audio/wav")