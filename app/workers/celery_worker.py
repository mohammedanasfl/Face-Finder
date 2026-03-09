import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from celery import Celery
import os
import re
import gdown
from celery import Celery
from app.jobs.import_drive_job import update_job_progress
from src.admin_processor import process_new_images
from config import RAW_IMAGES_PATH

# Initialize Celery app
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
if broker_url.startswith("rediss://") and "ssl_cert_reqs" not in broker_url:
    broker_url += "?ssl_cert_reqs=CERT_NONE"
    
celery_app = Celery("workers", broker=broker_url, backend=broker_url)
def parse_folder_id(input_string):
    """Extracts the folder ID if the user pastes a full Google Drive URL."""
    match = re.search(r'folders/([A-Za-z0-9_-]+)', input_string)
    if match:
        return match.group(1)
    return input_string

@celery_app.task(name="process_drive_folder")
def process_drive_folder_task(job_id: str, drive_folder_id: str):
    """
    Background Task: Uses gdown to pull a generic public Google Drive folder, 
    detects their faces, and appends them to FAISS.
    """
    try:
        update_job_progress(job_id, status="downloading")
        
        folder_id = parse_folder_id(drive_folder_id)
        url = f'https://drive.google.com/drive/folders/{folder_id}?usp=sharing'
        
        # Download the folder contents natively (returns a list of string filepaths)
        downloaded = gdown.download_folder(url, output=RAW_IMAGES_PATH, quiet=False, use_cookies=False)
        
        if not downloaded:
            update_job_progress(job_id, status="completed_no_images")
            return "No images found or folder not public."
            
        # Filter for actual images
        valid_extensions = {'.png', '.jpg', '.jpeg', '.JPG', '.PNG', '.JPEG'}
        image_paths = []
        for path in downloaded:
            if any(path.lower().endswith(ext.lower()) for ext in valid_extensions):
                image_paths.append(path)
                
        update_job_progress(job_id, images_downloaded=len(image_paths), status="processing")
        
        # 2. Run AI logic using the downloaded files
        if image_paths:
            faces_added = process_new_images(image_paths)
            update_job_progress(job_id, faces_detected=faces_added, status="completed")
            return f"Success: {faces_added} faces indexed"
        else:
            update_job_progress(job_id, status="failed_no_valid_images")
            return "Failed: No valid images found in folder"

    except Exception as e:
        update_job_progress(job_id, status=f"failed: {str(e)}")
        raise e
