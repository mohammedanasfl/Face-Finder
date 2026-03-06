# FaceFind: AI Event Photo Search

FaceFind is a complete full-stack AI platform built to instantly search massive event photo libraries using facial recognition. 

Upload a selfie, and the application's AI pipeline extracts facial embeddings to return every single original, high-quality event photo you appeared in.

![FaceFind UI Screenshot](https://via.placeholder.com/800x400.png?text=FaceFind+Premium+Dark+UI)

## 🚀 Features

- **AI Face Embeddings:** Powered by the state-of-the-art **InsightFace** (`buffalo_l`) model for extracting rich facial features.
- **Lightning-Fast Vector Search:** Uses **FAISS** (`IndexFlatIP`) with L2-Normalized Cosine Similarity for millisecond-speed matching across thousands of photos.
- **Smart Detection:** Automatically pads tightly cropped selfies so the detector never fails to recognize a face.
- **Modern Full-Stack Architecture:**
  - **Backend:** High-performance REST API built with **FastAPI**.
  - **Security:** Fully protected API endpoints using **JWT (JSON Web Tokens)**.
  - **Frontend:** Beautiful, responsive, premium Dark Mode SPA built with **React**, **Vite**, and **Vanilla CSS** (No external CSS wrappers used).
- **Duplicate Handling:** Automatically maps multiple detected faces back to their actual source photo and deduplicates the results so users only see unique event images.

---

## 🏗️ Project Architecture

```text
face-event-search/
├── data/
│   ├── raw_images/       # 1. Place your raw event photos here
│   ├── faces/            # 2. Automatically cropped faces are saved here
│   └── embeddings/       # 3. Vector embeddings (.npy & .pkl)
├── database/             # 4. Compiled FAISS index (.bin)
├── src/
│   ├── admin_processor.py# Script: Incrementally processes uploaded images
│   ├── face_detector.py  # Script: Detects & crops faces from raw_images
│   ├── face_embedder.py  # Script: Converts crops to vector embeddings
│   ├── build_index.py    # Script: Normalizes vectors and builds FAISS index
│   ├── search_face.py    # CLI tool for testing searches globally
│   └── utils.py          # Shared helpers and model loading
├── app/                  # FastAPI Backend Server
│   ├── app.py            # Main API routes and CORS config
│   ├── auth.py           # JWT Bearer dependency injection
│   └── security.py       # JWT creation and role logic
├── frontend/react-app/src  # React SPA
│   ├── components/       # Atomic UI building blocks
│   ├── pages/            # Application views (Login, Dashboard)
│   ├── services/         # Axios API interceptors and clients
│   ├── styles/           # Decoupled Vanilla CSS modules
│   ├── utils/            # Route protection
│   ├── App.jsx           # React Router implementation
│   └── main.jsx
├── config.py
└── requirements.txt
```

---

## 🛠️ Installation & Setup

### 1. Backend & AI Setup

Create a Python environment and install the required machine learning and API libraries:
```bash
python -m venv venv
venv\Scripts\activate   # Or `source venv/bin/activate` on Linux/Mac
pip install -r requirements.txt
```

### 2. Prepare Your Image Database (Initial Load)

Simply drop your raw event photos (JPG, PNG) into the `data/raw_images` folder.

Next, run the three pipeline scripts in order to process the images, extract the AI embeddings, and build the FAISS vector database:

```bash
# Finds every face in every photo and crops them into data/faces/
python src/face_detector.py

# Converts the crops into vector arrays
python src/face_embedder.py

# Normalizes the arrays and compiles the FAISS index database
python src/build_index.py
```

*Note: You only need to run these scripts for the initial bulk data load. Future event photos can be uploaded via the Admin Dashboard UI!*

---

## 💻 Running the Application

This is a decoupled application, meaning you must run both the backend API and the frontend UI at the same time.

### Start the FastAPI Backend
In your initialized python environment:
```bash
uvicorn app.app:app --reload
```
*The API will start running on `http://localhost:8000`.*

### Start the React Frontend
Open a **new** terminal window:
```bash
cd frontend/react-app
npm install
npm run dev
```
*The UI will start running on `http://localhost:5173`.*

---

## 🔑 Usage Guide

1. Open `http://localhost:5173` in your browser.
2. The system is protected by JWT authentication with role-based access control.
   - **Admin Login:** Enter `admin-1234`
   - **User Login:** Enter `user-1234`
3. **If logged in as User:** You can upload a selfie or a clear headshot of a person into the upload zone to perform a Face Search.
4. **If logged in as Admin:** You gain access to the **Bulk Image Upload** portal. You can drag and drop hundreds of new event photos into the browser. The backend will automatically run the AI pipeline on the new images and append them to the FAISS index without needing to use the CLI.
5. The API will process the searched image, match the embeddings using Cosine Similarity, and return all the original high-resolution event photos the person is featured in!
