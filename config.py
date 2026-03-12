import os


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_allowed_origins() -> list[str]:
    raw_origins = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def get_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be a float") from exc


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_IMAGES_PATH = os.path.join(BASE_DIR, "data", "raw_images")
FACES_PATH = os.path.join(BASE_DIR, "data", "faces")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "data", "embeddings")
DATABASE_PATH = os.path.join(BASE_DIR, "database")
UPLOADS_PATH = os.path.join(BASE_DIR, "uploads")
LOCKS_PATH = os.path.join(BASE_DIR, "locks")

JWT_SECRET_KEY = get_required_env("JWT_SECRET_KEY")
ADMIN_SECRET_KEY = get_required_env("ADMIN_SECRET_KEY")
USER_SECRET_KEY = get_required_env("USER_SECRET_KEY")
CORS_ALLOW_ORIGINS = get_allowed_origins()
SEARCH_SIMILARITY_THRESHOLD = get_float_env("SEARCH_SIMILARITY_THRESHOLD", 0.40)

# Automatically create all required directories
for path in [RAW_IMAGES_PATH, FACES_PATH, EMBEDDINGS_PATH, DATABASE_PATH, UPLOADS_PATH, LOCKS_PATH]:
    os.makedirs(path, exist_ok=True)
