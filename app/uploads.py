import os
import re
import uuid
from pathlib import Path


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def build_server_filename(original_name: str, prefix: str = "upload") -> str:
    original_path = Path(original_name or "")
    extension = original_path.suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Unsupported file type. Allowed types: jpg, jpeg, png, webp")

    safe_stem = re.sub(r"[^A-Za-z0-9_-]+", "-", original_path.stem).strip("-") or prefix
    return f"{safe_stem}-{uuid.uuid4().hex}{extension}"


def save_upload_file(upload_file, destination_dir: str, prefix: str) -> str:
    server_filename = build_server_filename(upload_file.filename, prefix=prefix)
    destination_path = os.path.join(destination_dir, server_filename)
    with open(destination_path, "wb") as handle:
        while True:
            chunk = upload_file.file.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    upload_file.file.close()
    return destination_path
