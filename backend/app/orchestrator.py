import os, json, uuid, shutil
from app.audio_utils import normalize_audio
from app.diarization import run_diarization
from app.separation_concat import separate_by_speaker_concat

BASE = "outputs/jobs"

def process_audio_pipeline(audio_path: str):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job_dir = os.path.join(BASE, job_id)

    speakers_dir = os.path.join(job_dir, "speakers")
    previews_dir = os.path.join(job_dir, "previews")

    os.makedirs(speakers_dir, exist_ok=True)
    os.makedirs(previews_dir, exist_ok=True)

    normalized = normalize_audio(audio_path)
    shutil.copy(normalized, os.path.join(job_dir, "normalized.wav"))

    segments = run_diarization(normalized)
    with open(os.path.join(job_dir, "diarization.json"), "w") as f:
        json.dump(segments, f, indent=2)

    speaker_files = separate_by_speaker_concat(
        normalized, segments, speakers_dir
    )

    metadata = []
    for spk, file in speaker_files.items():
        duration = sum(
            s["end"] - s["start"]
            for s in segments if s["speaker"] == spk
        )
        metadata.append({
            "speaker_id": spk,
            "duration": round(duration, 2),
            "audio": file
        })

    with open(os.path.join(job_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    return {
        "job_id": job_id,
        "speakers": metadata
    }
