from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import Optional

# --- App Imports ---
from app.orchestrator import process_audio_pipeline
from app.demucs_runner import run_demucs
from app.denoise_runner import run_denoise
from app.zipper import zip_folder

app = FastAPI(title="Voice, Music & Audio Enhancer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Accept-Ranges", "Content-Range", "Content-Length"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# 1. VOICE SEPARATION
# =========================
@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    temp = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return process_audio_pipeline(temp)


# =========================
# 2. MUSIC SEPARATION
# =========================
@app.post("/separate-music")
async def separate_music(file: UploadFile = File(...)):
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        output_folder = run_demucs(temp_path)
        
        # Robust folder check (Standard vs Fine-Tuned)
        if not os.path.exists(output_folder):
            if "htdemucs" in output_folder:
                ft_folder = output_folder.replace("htdemucs", "htdemucs_ft")
                if os.path.exists(ft_folder):
                    output_folder = ft_folder
                else:
                    std_folder = output_folder.replace("htdemucs_ft", "htdemucs")
                    if os.path.exists(std_folder):
                         output_folder = std_folder
                    else:
                        raise HTTPException(500, "Demucs output folder missing")

        stems = []
        base_path = os.getcwd()

        for filename in os.listdir(output_folder):
            if filename.endswith(".wav"):
                full_path = os.path.join(output_folder, filename)
                rel_path = os.path.relpath(full_path, base_path).replace("\\", "/")
                
                stems.append({
                    "speaker_id": os.path.splitext(filename)[0].capitalize(),
                    "duration": "N/A", 
                    "audio": rel_path,
                    "type": "stem"
                })

        return {
            "job_id": os.path.basename(output_folder),
            "speakers": stems,
            "mode": "music"
        }

    except Exception as e:
        print(f"Separation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 3. AUDIO ENHANCER (NEW)
# =========================
@app.post("/enhance-audio")
async def enhance_audio(file: UploadFile = File(...)):
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        output_path, job_id = run_denoise(temp_path)
        
        base_path = os.getcwd()
        rel_path = os.path.relpath(output_path, base_path).replace("\\", "/")
        
        return {
            "job_id": job_id,
            "speakers": [{
                "speaker_id": "Enhanced Audio",
                "duration": "N/A",
                "audio": rel_path,
                "type": "enhanced"
            }],
            "mode": "clean"
        }

    except Exception as e:
        print(f"Enhance Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# FILE STREAMING
# =========================
@app.get("/download")
def download(file: str):
    file_path = os.path.normpath(file)
    if not file_path.startswith("outputs"):
         raise HTTPException(status_code=403, detail="Access denied")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=os.path.basename(file_path)
    )


# =========================
# ZIP DOWNLOADER (ALL MODES)
# =========================
@app.get("/jobs/{job_id}/download-all")
def download_all(job_id: str, mode: Optional[str] = "speech"):
    print(f"DEBUG: ZIP Request -> Job: {job_id} | Mode: {mode}")

    possible_paths = [
        # 1. Voice Mode
        os.path.join("outputs", "jobs", job_id, "speakers"),
        
        # 2. Music Mode (Standard)
        os.path.join("outputs", "demucs", "htdemucs", job_id),
        
        # 3. Music Mode (Fine-Tuned)
        os.path.join("outputs", "demucs", "htdemucs_ft", job_id),

        # 4. Enhancer Mode
        os.path.join("outputs", "enhanced", job_id),
        
        # 5. Fallbacks
        os.path.join("outputs", "jobs", job_id, "final"),
        os.path.join("outputs", "demucs", job_id)
    ]
    
    target_dir = None
    for p in possible_paths:
        if os.path.exists(p):
            target_dir = p
            break
            
    if not target_dir:
        print(f"ERROR: Could not find files for {job_id}")
        raise HTTPException(status_code=404, detail="Job files not found.")

    zip_name = f"{job_id}_files.zip"
    zip_path = os.path.join("outputs", zip_name)
    
    try:
        zip_folder(target_dir, zip_path)
    except Exception as e:
        print(f"Zip Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create zip.")

    return FileResponse(zip_path, filename=zip_name)
