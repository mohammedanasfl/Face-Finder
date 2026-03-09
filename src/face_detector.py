import os
import cv2
from insightface.app import FaceAnalysis

# Paths
RAW_IMAGES_PATH = "data/raw_images"
FACES_OUTPUT_PATH = "data/faces"

os.makedirs(FACES_OUTPUT_PATH, exist_ok=True)

# Load face detection model
app = FaceAnalysis(name="buffalo_l", allowed_modules=['detection', 'recognition'])
app.prepare(ctx_id=0, det_size=(640, 640))

def detect_faces():
    for image_name in os.listdir(RAW_IMAGES_PATH):

        image_path = os.path.join(RAW_IMAGES_PATH, image_name)

        if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        print(f"Processing {image_name}")

        img = cv2.imread(image_path)

        faces = app.get(img)

        h, w = img.shape[:2]

        for i, face in enumerate(faces):

            bbox = face.bbox.astype(int)

            x1, y1, x2, y2 = bbox

            # Clamp coordinates to image boundaries
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            cropped_face = img[y1:y2, x1:x2]

            # Skip if crop is empty (bbox was entirely out of bounds)
            if cropped_face.size == 0:
                print(f"  Skipping face {i+1} in {image_name} (empty crop after clamping)")
                continue

            face_filename = f"{os.path.splitext(image_name)[0]}_face{i+1}.jpg"

            save_path = os.path.join(FACES_OUTPUT_PATH, face_filename)

            cv2.imwrite(save_path, cropped_face)

        print(f"Detected {len(faces)} faces")


if __name__ == "__main__":
    detect_faces()