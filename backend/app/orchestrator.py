import os
import json
import uuid
import shutil

from app.audio_utils import normalize_audio
from app.diarization import run_diarization
from app.separation_concat import separate_by_speaker_concat

BASE_DIR = "outputs/jobs"


def process_audio_pipeline(audio_path: str):
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job_dir = os.path.join(BASE_DIR, job_id)

    speakers_dir = os.path.join(job_dir, "speakers")
    os.makedirs(speakers_dir, exist_ok=True)

    normalized_path = normalize_audio(audio_path)
    shutil.copy(normalized_path, os.path.join(job_dir, "normalized.wav"))

    segments = run_diarization(normalized_path)
    with open(os.path.join(job_dir, "diarization.json"), "w") as f:
        json.dump(segments, f, indent=2)

    speaker_files = separate_by_speaker_concat(
        normalized_path,
        segments,
        speakers_dir
    )

    metadata = []
    for speaker_id, file_path in speaker_files.items():
        duration = sum(
            s["end"] - s["start"]
            for s in segments if s["speaker"] == speaker_id
        )

        metadata.append({
            "speaker_id": speaker_id,
            "duration": round(duration, 2),
            "audio": file_path
        })

    with open(os.path.join(job_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    return {
        "job_id": job_id,
        "speakers": metadata
    }
