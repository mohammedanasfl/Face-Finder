import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from celery import Celery
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.jobs.import_drive_job import update_job_progress
from src.admin_processor import process_new_images
from config import RAW_IMAGES_PATH

# Initialize Celery app
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("workers", broker=broker_url, backend=broker_url)

# In a real environment, you'd mount a credentials.json via Docker secrets
# Using a fallback to support public folders if credentials aren't provided
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

def get_drive_service():
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)
    else:
        # Fallback for public API key if explicit OAuth isn't provided
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            return build('drive', 'v3', developerKey=api_key)
        else:
            raise Exception("No Google Drive credentials or API key found. Cannot proceed.")

def download_file(service, file_id, file_name):
    """Downloads a single file from Google Drive."""
    try:
        request = service.files().get_media(fileId=file_id)
        save_path = os.path.join(RAW_IMAGES_PATH, file_name)
        
        # Don't re-download if we already grabbed it
        if os.path.exists(save_path):
            return save_path

        with open(save_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        return save_path
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")
        return None

@celery_app.task(name="process_drive_folder")
def process_drive_folder_task(job_id: str, drive_folder_id: str):
    """
    Background Task: Connects to Drive, downloads all images, 
    detects their faces, and appends them to FAISS.
    """
    try:
        service = get_drive_service()
        
        # 1. Map files inside the directory
        query = f"'{drive_folder_id}' in parents and mimeType contains 'image/' and trashed = false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            update_job_progress(job_id, status="completed_no_images")
            return "No images found in folder"

        total_files = len(items)
        downloaded_paths = []
        downloaded_count = 0

        # Create a threadpool to speed up bulk API downloading
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for item in items:
                futures.append(executor.submit(download_file, service, item['id'], item['name']))
            
            for future in futures:
                path = future.result()
                if path:
                    downloaded_paths.append(path)
                    downloaded_count += 1
                    # Progress tick natively into Redis
                    update_job_progress(job_id, images_downloaded=downloaded_count)

        # 2. Run AI logic using the downloaded files
        if downloaded_paths:
            faces_added = process_new_images(downloaded_paths)
            update_job_progress(job_id, faces_detected=faces_added, status="completed")
            return f"Success: {faces_added} faces indexed"
        else:
            update_job_progress(job_id, status="failed_downloads")
            return "Failed to download any images"

    except Exception as e:
        update_job_progress(job_id, status=f"failed: {str(e)}")
        raise e
