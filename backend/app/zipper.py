import zipfile
import os

def zip_folder(folder_path: str, zip_path: str):
    # CHANGED: Use ZIP_STORED instead of ZIP_DEFLATED
    # This skips compression (which is slow for audio) and just packages the files instantly.
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)

    return zip_path