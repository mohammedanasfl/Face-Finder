import os
import re

import gdown

from app.celery_app import celery_app
from app.jobs.import_drive_job import fail_job, update_job_progress
from config import RAW_IMAGES_PATH
from src.admin_processor import process_new_images


def parse_folder_id(input_string):
    """Extracts the folder ID if the user pastes a full Google Drive URL."""
    match = re.search(r"folders/([A-Za-z0-9_-]+)", input_string)
    if match:
        return match.group(1)
    return input_string


def _filter_image_paths(paths):
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    return [
        path
        for path in paths
        if any(path.lower().endswith(ext) for ext in valid_extensions)
    ]


@celery_app.task(name="process_uploaded_images")
def process_uploaded_images_task(job_id: str, image_paths: list[str]):
    try:
        update_job_progress(
            job_id,
            total_files=len(image_paths),
            images_received=len(image_paths),
            status="processing",
        )
        faces_added = process_new_images(image_paths)
        update_job_progress(job_id, faces_indexed=faces_added, status="completed")
        return {"faces_indexed": faces_added}
    except Exception as exc:
        fail_job(job_id, str(exc))
        raise


@celery_app.task(name="process_drive_folder")
def process_drive_folder_task(job_id: str, drive_folder_id: str):
    """
    Background task: downloads a public Google Drive folder and indexes the images.
    """
    try:
        update_job_progress(job_id, status="downloading")

        folder_id = parse_folder_id(drive_folder_id)
        url = f"https://drive.google.com/drive/folders/{folder_id}?usp=sharing"
        downloaded = gdown.download_folder(
            url,
            output=RAW_IMAGES_PATH,
            quiet=False,
            use_cookies=False,
            remaining_ok=True,
        )

        if not downloaded:
            update_job_progress(job_id, status="completed_no_images")
            return {"faces_indexed": 0}

        image_paths = _filter_image_paths(downloaded)
        update_job_progress(
            job_id,
            total_files=len(downloaded),
            images_downloaded=len(image_paths),
            status="processing",
        )

        if not image_paths:
            fail_job(job_id, "No valid image files found in the Drive folder")
            return {"faces_indexed": 0}

        faces_added = process_new_images(image_paths)
        update_job_progress(job_id, faces_indexed=faces_added, status="completed")
        return {"faces_indexed": faces_added}
    except Exception as exc:
        fail_job(job_id, str(exc))
        raise
