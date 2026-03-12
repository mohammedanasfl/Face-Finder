import os
import cv2
import numpy as np
import pickle
import tempfile
from src.utils import get_model
from src.build_index import build_faiss_index
from src.file_lock import file_lock
from config import FACES_PATH, EMBEDDINGS_PATH, LOCKS_PATH


INDEX_LOCK_PATH = os.path.join(LOCKS_PATH, "indexing.lock")


def _atomic_save_numpy(path, array):
    with tempfile.NamedTemporaryFile(delete=False, dir=os.path.dirname(path), suffix=".npy") as temp_file:
        temp_path = temp_file.name
    np.save(temp_path, array)
    os.replace(temp_path, path)


def _atomic_save_pickle(path, value):
    with tempfile.NamedTemporaryFile(delete=False, dir=os.path.dirname(path), suffix=".pkl") as temp_file:
        temp_path = temp_file.name
    with open(temp_path, "wb") as handle:
        pickle.dump(value, handle)
    os.replace(temp_path, path)

def process_new_images(new_image_paths):
    """
    Processes a list of newly uploaded images:
    1. Detects faces and saves crops.
    2. Generates embeddings.
    3. Appends to embeddings.npy and image_paths.pkl.
    4. Rebuilds the FAISS index.
    """
    app = get_model()
    
    new_embeddings = []
    new_face_filenames = []
    
    # Process each new image
    for image_path in new_image_paths:
        image_name = os.path.basename(image_path)
        img = cv2.imread(image_path)
        if img is None:
            continue
            
        faces = app.get(img)
        h, w = img.shape[:2]
        
        for i, face in enumerate(faces):
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            cropped_face = img[y1:y2, x1:x2]
            if cropped_face.size == 0:
                continue
                
            face_filename = f"{os.path.splitext(image_name)[0]}_face{i+1}.jpg"
            save_path = os.path.join(FACES_PATH, face_filename)
            cv2.imwrite(save_path, cropped_face)
            
            # Generate embedding for this face
            # Pad the cropped face with a black border so the detector doesn't ignore it
            padded_img = cv2.copyMakeBorder(cropped_face, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            crop_faces = app.get(padded_img)
            
            if len(crop_faces) > 0:
                embedding = crop_faces[0].embedding
                new_embeddings.append(embedding)
                new_face_filenames.append(face_filename)
                
    if not new_embeddings:
        return 0 # No new faces found
        
    npy_path = os.path.join(EMBEDDINGS_PATH, "embeddings.npy")
    pkl_path = os.path.join(EMBEDDINGS_PATH, "image_paths.pkl")

    with file_lock(INDEX_LOCK_PATH):
        if os.path.exists(npy_path) and os.path.exists(pkl_path):
            existing_embeddings = np.load(npy_path)
            with open(pkl_path, "rb") as f:
                existing_paths = pickle.load(f)

            updated_embeddings = np.vstack((existing_embeddings, np.array(new_embeddings)))
            updated_paths = existing_paths + new_face_filenames
        else:
            updated_embeddings = np.array(new_embeddings)
            updated_paths = new_face_filenames

        _atomic_save_numpy(npy_path, updated_embeddings)
        _atomic_save_pickle(pkl_path, updated_paths)

        # Rebuild FAISS index while holding the same lock so readers never see partial writes.
        build_faiss_index()

    return len(new_embeddings)
