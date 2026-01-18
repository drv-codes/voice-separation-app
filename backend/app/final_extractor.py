import os
import subprocess
from typing import List


def extract_single_speaker_concat(
    audio_path: str,
    segments: List[dict],
    output_dir: str,
    speaker_id: str
) -> str:

    os.makedirs(output_dir, exist_ok=True)

    segments = sorted(segments, key=lambda x: x["start"])

    temp_files = []
    list_file = os.path.join(output_dir, f"{speaker_id}_files.txt")
    final_output = os.path.join(output_dir, f"{speaker_id}.wav")

    for i, seg in enumerate(segments):
        start = float(seg["start"])
        end = float(seg["end"])

        if end <= start:
            continue

        temp_wav = os.path.join(output_dir, f"{speaker_id}_{i}.wav")
        temp_files.append(temp_wav)

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-ss", str(start),
                "-to", str(end),
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                temp_wav
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )

    if not temp_files:
        raise RuntimeError(f"No valid segments for {speaker_id}")

    with open(list_file, "w", encoding="utf-8") as f:
        for wav in temp_files:
            f.write(f"file '{os.path.abspath(wav)}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "pcm_s16le",
            final_output
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    for wav in temp_files:
        if os.path.exists(wav):
            os.remove(wav)

    if os.path.exists(list_file):
        os.remove(list_file)

    return final_output
