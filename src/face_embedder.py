import os
import cv2
import numpy as np
import pickle
from insightface.app import FaceAnalysis

FACES_PATH = "data/faces"
EMBEDDINGS_PATH = "data/embeddings"

os.makedirs(EMBEDDINGS_PATH, exist_ok=True)

# Load insightface model
app = FaceAnalysis(name="buffalo_l", allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=0, det_size=(640,640))

embeddings = []
image_paths = []

def generate_embeddings():

    for image_name in os.listdir(FACES_PATH):

        image_path = os.path.join(FACES_PATH, image_name)

        if not image_name.lower().endswith((".jpg",".jpeg",".png")):
            continue

        print("Processing:", image_name)

        img = cv2.imread(image_path)

        # Pad the cropped face with a black border so the detector doesn't ignore it
        padded_img = cv2.copyMakeBorder(img, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        faces = app.get(padded_img)

        if len(faces) == 0:
            continue

        embedding = faces[0].embedding

        embeddings.append(embedding)
        image_paths.append(image_name)

    embeddings_array = np.array(embeddings)

    np.save(os.path.join(EMBEDDINGS_PATH, "embeddings.npy"), embeddings_array)

    with open(os.path.join(EMBEDDINGS_PATH, "image_paths.pkl"), "wb") as f:
        pickle.dump(image_paths, f)

    print("Embeddings saved successfully")

if __name__ == "__main__":
    generate_embeddings()