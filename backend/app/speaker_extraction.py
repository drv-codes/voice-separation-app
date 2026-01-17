import os
from collections import defaultdict
from pydub import AudioSegment


def extract_speakers(audio_path: str, segments: list, output_dir: str):
    """
    Extract one audio file per speaker using diarization segments.
    Overlapping speech is allowed.
    """

    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)

    os.makedirs(output_dir, exist_ok=True)

    audio = AudioSegment.from_file(audio_path)

    speaker_audio = defaultdict(AudioSegment.empty)

    for seg in segments:
        speaker = seg["speaker"]
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)

        clip = audio[start_ms:end_ms]
        speaker_audio[speaker] += clip

    output_files = []

    for speaker, combined_audio in speaker_audio.items():
        out_path = os.path.join(output_dir, f"{speaker}.wav")
        combined_audio.export(out_path, format="wav")
        output_files.append(out_path)

    return output_files
