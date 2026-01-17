import os
import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=HF_TOKEN
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
pipeline.to(DEVICE)

def run_diarization(audio_path: str):
    diarization = pipeline(audio_path)

    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start": round(float(turn.start), 2),
            "end": round(float(turn.end), 2)
        })

    return segments
