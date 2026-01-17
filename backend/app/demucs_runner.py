import os
import subprocess

def run_demucs(input_audio: str, output_base: str = "outputs/demucs"):
    if not os.path.exists(input_audio):
        raise FileNotFoundError(f"Audio not found: {input_audio}")

    song_name = os.path.splitext(os.path.basename(input_audio))[0]
    
    os.makedirs(output_base, exist_ok=True)

    command = [
        "demucs",
        "-n", "htdemucs",     # Standard Model (Fastest)
        "--device", "cuda",   # Use GPU if available
        "--int24",            # KEEP THIS: Fixes "muted" audio issue
        "--out", output_base,
        input_audio
    ]

    print(f"Running Standard Demucs (24-bit) on {input_audio}...")
    subprocess.run(command, check=True)

    # Return the specific output folder
    final_output_dir = os.path.join(output_base, "htdemucs", song_name)
    
    return final_output_dir