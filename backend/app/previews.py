import os
import subprocess

def generate_speaker_previews(audio_path, segments, output_dir, duration=5):
    os.makedirs(output_dir, exist_ok=True)

    previews = {}
    seen = set()

    for seg in segments:
        spk = seg["speaker"]
        if spk in seen:
            continue

        preview = os.path.join(output_dir, f"{spk}_preview.wav")

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-ss", str(seg["start"]),
                "-t", str(duration),
                preview
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        previews[spk] = preview
        seen.add(spk)

    return previews
