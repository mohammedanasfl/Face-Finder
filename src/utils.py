import cv2
import numpy as np
import faiss
import pickle
import os
from insightface.app import FaceAnalysis

_app = None

def get_model():
    global _app
    if _app is None:
        _app = FaceAnalysis(name="buffalo_l")
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app

def load_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    return img

def get_embedding(image_path):
    app = get_model()
    img = load_image(image_path)
    # Pad the image with a black border to ensure tightly cropped selfies are still detected
    padded_img = cv2.copyMakeBorder(img, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    faces = app.get(padded_img)
    if len(faces) == 0:
        return None
    return faces[0].embedding

def run_faiss_search(embedding, index_path, image_map_path, top_k=1000):
    index = faiss.read_index(index_path)
    with open(image_map_path, "rb") as f:
        image_map = pickle.load(f)
    query = np.array([embedding]).astype("float32")
    
    # Normalize query for Cosine Similarity
    faiss.normalize_L2(query)
    
    distances, indices = index.search(query, top_k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        results.append({"face": image_map[idx], "distance": float(dist)})
    return results
