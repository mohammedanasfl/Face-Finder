import os
import re
import uuid
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.auth import get_current_admin, get_current_user, get_current_regular_user
from app.celery_app import celery_app
from app.jobs.import_drive_job import get_job_status, initialize_job
from app.security import ADMIN_SECRET_KEY, USER_SECRET_KEY, create_access_token
from app.uploads import save_upload_file
from config import (
    CORS_ALLOW_ORIGINS,
    RAW_IMAGES_PATH,
    SEARCH_SIMILARITY_THRESHOLD,
    UPLOADS_PATH,
)


os.makedirs(UPLOADS_PATH, exist_ok=True)
os.makedirs(RAW_IMAGES_PATH, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.mount("/raw_images", StaticFiles(directory=RAW_IMAGES_PATH), name="raw_images")


class LoginRequest(BaseModel):
    secret_key: str


class DriveImportRequest(BaseModel):
    drive_folder_id: str


def get_original_image_name(face_filename, raw_images_list):
    base_name = re.sub(r"_face\d+\.jpg$", "", face_filename)
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"]:
        if (base_name + ext) in raw_images_list:
            return base_name + ext
    return None


def perform_face_search(image_path: str):
    from src.search_face import search_face

    return search_face(image_path)


@app.post("/login")
def login(request: LoginRequest):
    if request.secret_key == ADMIN_SECRET_KEY:
        role = "admin"
        username = "admin"
    elif request.secret_key == USER_SECRET_KEY:
        role = "user"
        username = "user"
    else:
        raise HTTPException(status_code=401, detail="Invalid secret key")

    access_token = create_access_token(data={"sub": username, "role": role})
    return {"access_token": access_token, "token_type": "bearer", "role": role}


@app.post("/admin/upload-images")
async def upload_event_images(
    files: List[UploadFile] = File(...),
    current_admin: dict = Depends(get_current_admin),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")

    saved_paths = []
    try:
        for upload in files:
            saved_paths.append(save_upload_file(upload, RAW_IMAGES_PATH, prefix="event"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job_id = str(uuid.uuid4())
    initialize_job(job_id, job_type="upload")
    celery_app.send_task("process_uploaded_images", args=[job_id, saved_paths])

    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "queued",
            "images_received": len(saved_paths),
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search-face")
async def search_face_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_regular_user),
):
    try:
        save_path = save_upload_file(file, UPLOADS_PATH, prefix="query")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        results = perform_face_search(save_path)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)

    raw_images_list = set(os.listdir(RAW_IMAGES_PATH)) if os.path.exists(RAW_IMAGES_PATH) else set()

    ranked_matches = []
    seen = set()

    for result in results:
        similarity = float(result["distance"])
        if similarity < SEARCH_SIMILARITY_THRESHOLD:
            continue

        orig_name = get_original_image_name(result["face"], raw_images_list)
        if not orig_name or orig_name in seen:
            continue

        seen.add(orig_name)
        ranked_matches.append({"filename": orig_name, "score": round(similarity, 4)})

    if not ranked_matches:
        from config import DATABASE_PATH
        index_exists = os.path.exists(os.path.join(DATABASE_PATH, "faiss_index.bin"))
        if not index_exists:
            raise HTTPException(
                status_code=404,
                detail="No images have been indexed yet. Please import event photos via the Admin panel first."
            )
        raise HTTPException(status_code=404, detail="No matching faces found.")

    return JSONResponse(
        content={
            "threshold": SEARCH_SIMILARITY_THRESHOLD,
            "matches": [match["filename"] for match in ranked_matches],
            "results": ranked_matches,
        }
    )


@app.post("/admin/import-drive")
async def import_drive_folder(
    request: DriveImportRequest,
    current_admin: dict = Depends(get_current_admin),
):
    try:
        job_id = str(uuid.uuid4())
        initialize_job(job_id, job_type="drive_import")
        celery_app.send_task("process_drive_folder", args=[job_id, request.drive_folder_id])

        return JSONResponse(content={"job_id": job_id, "status": "queued"})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/admin/job-status/{job_id}")
async def get_drive_import_status(
    job_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    try:
        status_data = get_job_status(job_id)
        return JSONResponse(content=status_data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
