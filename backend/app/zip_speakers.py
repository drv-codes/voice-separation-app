import os
import zipfile

def zip_speakers_only(job_dir: str) -> str:
    """
    Creates a ZIP containing ONLY final speaker audio files.
    """
    speakers_dir = os.path.join(job_dir, "speakers")
    zip_path = os.path.join(job_dir, "speakers_only.zip")

    if not os.path.exists(speakers_dir):
        raise FileNotFoundError("Speakers folder not found")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(speakers_dir):
            if file.endswith(".wav"):
                full_path = os.path.join(speakers_dir, file)
                zipf.write(
                    full_path,
                    arcname=os.path.join("speakers", file)
                )

    return zip_path
