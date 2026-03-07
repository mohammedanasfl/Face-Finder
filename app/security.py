import os
from datetime import datetime, timedelta
from jose import jwt

# Secret keys for signing and authentication (pulled from environment if available)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_signing_secret_key_here")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "admin-1234")
USER_SECRET_KEY = os.getenv("USER_SECRET_KEY", "user-1234")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
