import numpy as np
import faiss
import pickle
import os

EMBEDDINGS_PATH = "data/embeddings"
DATABASE_PATH = "database"

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

    faiss.write_index(index, os.path.join(DATABASE_PATH, "faiss_index.bin"))

    with open(os.path.join(DATABASE_PATH, "image_map.pkl"), "wb") as f:
        pickle.dump(image_paths, f)

    print("FAISS index saved successfully")

if __name__ == "__main__":
    build_faiss_index()