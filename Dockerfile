# Use lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required by OpenCV and FAISS
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the uvicorn ASGI server
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
