import os
import subprocess
import uuid

def run_denoise(input_audio: str, output_base: str = "outputs/enhanced"):
    """
    Runs FFmpeg Noise Reduction and Loudness Normalization.
    Creates a specific job folder to make zipping easier.
    """
    if not os.path.exists(input_audio):
        raise FileNotFoundError(f"Audio not found: {input_audio}")

    # Generate unique Job ID
    job_id = f"clean_{uuid.uuid4().hex[:8]}"
    
    # Create a specific folder for this job: outputs/enhanced/{job_id}
    job_dir = os.path.join(output_base, job_id)
    os.makedirs(job_dir, exist_ok=True)

    filename = os.path.basename(input_audio)
    name, _ = os.path.splitext(filename)
    
    # Output file path
    output_path = os.path.join(job_dir, f"{name}_cleaned.wav")

    print(f"Running Audio Enhancement on {input_audio}...")

    # FFmpeg Filter Chain:
    # 1. afftdn=nf=-25: Noise Floor reduction (-25dB)
    # 2. loudnorm: Professional Loudness Normalization (EBU R128)
    command = [
        "ffmpeg", "-y",
        "-i", input_audio,
        "-af", "afftdn=nf=-25,loudnorm",
        "-ac", "2",           # Stereo
        "-ar", "44100",       # 44.1kHz
        "-c:a", "pcm_s24le",  # 24-bit WAV
        output_path
    ]

    subprocess.run(command, check=True)

    return output_path, job_id