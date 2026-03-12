import numpy as np
import faiss
import pickle
import os
import tempfile
from config import EMBEDDINGS_PATH, DATABASE_PATH

os.makedirs(DATABASE_PATH, exist_ok=True)

def build_faiss_index():
    embeddings = np.load(os.path.join(EMBEDDINGS_PATH, "embeddings.npy"))

    with open(os.path.join(EMBEDDINGS_PATH, "image_paths.pkl"), "rb") as f:
        image_paths = pickle.load(f)

    print("Embeddings shape:", embeddings.shape)

    dimension = embeddings.shape[1]

    # Normalize embeddings for Cosine Similarity
    faiss.normalize_L2(embeddings)

    # Use Inner Product (which equals Cosine Similarity for normalized vectors)
    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print("Total vectors indexed:", index.ntotal)

    with tempfile.NamedTemporaryFile(delete=False, dir=DATABASE_PATH, suffix=".bin") as temp_index_file:
        temp_index_path = temp_index_file.name
    faiss.write_index(index, temp_index_path)
    os.replace(temp_index_path, os.path.join(DATABASE_PATH, "faiss_index.bin"))

    with tempfile.NamedTemporaryFile(delete=False, dir=DATABASE_PATH, suffix=".pkl") as temp_map_file:
        temp_map_path = temp_map_file.name
    with open(temp_map_path, "wb") as f:
        pickle.dump(image_paths, f)
    os.replace(temp_map_path, os.path.join(DATABASE_PATH, "image_map.pkl"))

    print("FAISS index saved successfully")

if __name__ == "__main__":
    build_faiss_index()
