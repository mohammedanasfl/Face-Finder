import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_IMAGES_PATH = os.path.join(BASE_DIR, "data", "raw_images")
FACES_PATH = os.path.join(BASE_DIR, "data", "faces")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "data", "embeddings")
DATABASE_PATH = os.path.join(BASE_DIR, "database")
UPLOADS_PATH = os.path.join(BASE_DIR, "uploads")

# Automatically create all required directories
for path in [RAW_IMAGES_PATH, FACES_PATH, EMBEDDINGS_PATH, DATABASE_PATH, UPLOADS_PATH]:
    os.makedirs(path, exist_ok=True)
