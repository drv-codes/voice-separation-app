import os
import subprocess
from collections import defaultdict

def separate_by_speaker_concat(audio_path, segments, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    speakers = defaultdict(list)
    for s in segments:
        speakers[s["speaker"]].append(s)

    outputs = {}

    for speaker, segs in speakers.items():
        list_file = os.path.join(output_dir, f"{speaker}_list.txt")
        final_audio = os.path.join(output_dir, f"{speaker}.wav")

        with open(list_file, "w") as f:
            for i, seg in enumerate(segs):
                temp = os.path.join(output_dir, f"{speaker}_{i}.wav")

                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", audio_path,
                    "-ss", str(seg["start"]),
                    "-to", str(seg["end"]),
                    temp
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                f.write(f"file '{os.path.abspath(temp)}'\n")

        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            final_audio
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # cleanup
        for i in range(len(segs)):
            os.remove(os.path.join(output_dir, f"{speaker}_{i}.wav"))
        os.remove(list_file)

        outputs[speaker] = final_audio

    return outputs
