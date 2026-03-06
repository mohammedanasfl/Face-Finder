import os
import sys
import shutil
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UPLOADS_PATH, RAW_IMAGES_PATH, FACES_PATH
from src.search_face import search_face
from src.admin_processor import process_new_images
from app.security import create_access_token, ADMIN_SECRET_KEY, USER_SECRET_KEY
from app.auth import get_current_user, get_current_admin

os.makedirs(UPLOADS_PATH, exist_ok=True)

app = FastAPI()

# Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the raw images directory so the frontend can display matched full photos
app.mount("/raw_images", StaticFiles(directory=RAW_IMAGES_PATH), name="raw_images")

class LoginRequest(BaseModel):
    secret_key: str

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
    current_admin: dict = Depends(get_current_admin)
):
    saved_paths = []
    # Save the original event photos
    for file in files:
        save_path = os.path.join(RAW_IMAGES_PATH, file.filename)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        saved_paths.append(save_path)
        
    # Process only the newly uploaded images and rebuild FAISS index
    faces_added = process_new_images(saved_paths)
    
    return JSONResponse(status_code=200, content={
        "message": f"Successfully processed {len(saved_paths)} images and indexed {faces_added} faces.",
        "images_uploaded": len(saved_paths),
        "faces_indexed": faces_added
    })

@app.get("/health")
def health():
    return {"status": "ok"}

import re

def get_original_image_name(face_filename, raw_images_list):
    base_name = re.sub(r'_face\d+\.jpg$', '', face_filename)
    for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
        if (base_name + ext) in raw_images_list:
            return base_name + ext
    return base_name + ".jpg"

@app.post("/search-face")
async def search_face_endpoint(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    save_path = os.path.join(UPLOADS_PATH, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    results = search_face(save_path)

    raw_images_list = set(os.listdir(RAW_IMAGES_PATH)) if os.path.exists(RAW_IMAGES_PATH) else set()
    
    unique_matches = []
    seen = set()
    
    # Cosine Similarity threshold (higher is better, 1.0 is exact match)
    threshold = 0.40

    for idx, r in enumerate(results):
        if idx < 20:
            print(f"DEBUG: Face {r['face']} has similarity {r['distance']:.4f}")
            
        # For Inner Product / Cosine Similarity, we want values GREATER than the threshold
        if r["distance"] > threshold:
            orig_name = get_original_image_name(r["face"], raw_images_list)
            if orig_name not in seen:
                seen.add(orig_name)
                unique_matches.append(orig_name)

    if not unique_matches:
        raise HTTPException(status_code=404, detail="No matching faces found.")

    return JSONResponse(content={"matches": unique_matches})
