from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.db.mongo import users_collection, admins_collection, blacklist_collection
import uuid
from typing import Union

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configs
SECRET_KEY = os.getenv("JWT_SECRET", "secret123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())  # Unique token ID
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Union[dict, None]:
    """Decode token, return claims or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user_with_role(role: str):
    """FastAPI dependency to protect endpoints by role."""
    def verify_token(token: str = Depends(oauth2_scheme)):
        try:
            # ✅ FIXED: Moved payload definition BEFORE using it
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            jti = payload.get("jti")
            if jti and blacklist_collection.find_one({"jti": jti}):
                raise HTTPException(status_code=401, detail="Token is blacklisted")

            username = payload.get("sub")
            user_role = payload.get("role")
            if not username or not user_role:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            if user_role != role:
                raise HTTPException(status_code=403, detail="Insufficient role")

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Lookup user/admin in DB
        collection = admins_collection if role == "admin" else users_collection
        user = collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

    return verify_token
