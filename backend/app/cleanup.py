import os
import shutil
import threading
import time

def delete_path(path: str):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)

def schedule_job_cleanup(job_dir: str, delay_minutes: int = 30):
    
    def _cleanup():
        time.sleep(delay_minutes * 60)
        delete_path(job_dir)

    t = threading.Thread(target=_cleanup, daemon=True)
    t.start()
