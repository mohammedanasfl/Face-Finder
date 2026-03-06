from datetime import datetime, timedelta
from jose import jwt

# User Login Keys (Input by the user to authenticate)
ADMIN_SECRET_KEY = "admin-1234"
USER_SECRET_KEY = "user-1234"

# Cryptographic Key for signing the JWT (Do NOT change this once tokens are issued)
JWT_SECRET_KEY = "super-secret-cryptographic-jwt-signature-key-change-me-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
