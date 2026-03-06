import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH
from src.utils import get_embedding, run_faiss_search

FAISS_INDEX_PATH = os.path.join(DATABASE_PATH, "faiss_index.bin")
IMAGE_MAP_PATH = os.path.join(DATABASE_PATH, "image_map.pkl")

def search_face(query_image_path):
    embedding = get_embedding(query_image_path)
    if embedding is None:
        return []
    return run_faiss_search(embedding, FAISS_INDEX_PATH, IMAGE_MAP_PATH, top_k=1000)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/search_face.py <path_to_query_image>")
        sys.exit(1)
    results = search_face(sys.argv[1])
    for r in results:
        print(f"{r['face']}  (distance: {r['distance']:.4f})")
