import os
import subprocess
from collections import defaultdict

OUTPUT_ROOT = os.path.join("outputs", "separation")
PREVIEW_DURATION = 5


def separate_by_speaker(audio_path: str, segments: list):
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = os.path.join(OUTPUT_ROOT, filename)
    os.makedirs(output_dir, exist_ok=True)

    speakers = defaultdict(list)
    for seg in segments:
        speakers[seg["speaker"]].append(seg)

    created_files = []
    preview_files = {}

    for speaker, segs in speakers.items():
        speaker_file = os.path.join(output_dir, f"{speaker}.wav")
        concat_list = os.path.join(output_dir, f"{speaker}_list.txt")

        temp_segments = []

        # 1️⃣ Cut segments
        for i, seg in enumerate(segs):
            temp_seg = os.path.join(output_dir, f"{speaker}_{i}.wav")

            subprocess.run([
                "ffmpeg", "-y",
                "-i", audio_path,
                "-ss", str(seg["start"]),
                "-to", str(seg["end"]),
                "-ar", "44100",
                "-ac", "2",
                "-c:a", "pcm_s16le",
                temp_seg
            ], check=True)

            temp_segments.append(temp_seg)

        if not temp_segments:
            continue

        # 2️⃣ Write concat list
        with open(concat_list, "w", encoding="utf-8", newline="\n") as f:
            for seg_file in temp_segments:
                f.write(f"file '{os.path.abspath(seg_file)}'\n")

        # 3️⃣ Concatenate
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-ar", "44100",
            "-ac", "2",
            speaker_file
        ], check=True)

        # 4️⃣ Cleanup
        for f in temp_segments:
            os.remove(f)
        os.remove(concat_list)

        created_files.append(speaker_file)

        # 5️⃣ Preview
        preview_path = os.path.join(output_dir, f"{speaker}_preview.wav")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", speaker_file,
            "-t", str(PREVIEW_DURATION),
            preview_path
        ], check=True)

        preview_files[speaker] = preview_path

    return {
        "speaker_files": created_files,
        "previews": preview_files,
        "output_dir": output_dir
    }


