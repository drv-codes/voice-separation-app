import subprocess
import os
import uuid

NORMALIZED_DIR = "outputs/normalized"
os.makedirs(NORMALIZED_DIR, exist_ok=True)

def normalize_audio(input_path: str) -> str:
    output_path = os.path.join(
        NORMALIZED_DIR,
        f"{uuid.uuid4().hex}.wav"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    return output_path
