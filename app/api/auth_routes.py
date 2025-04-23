from fastapi import APIRouter, HTTPException, Request, Depends, Form
from app.models.user import UserCreate, UserLogin
from app.services.auth_service import register_user, login_user, login_admin
from app.db.mongo import blacklist_collection, users_docs_collection
from app.auth.jwt_handler import decode_access_token, oauth2_scheme
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("/signup")
def signup(user: UserCreate):
    try:
        token = register_user(user)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(user: UserLogin):
    try:
        token = login_user(user)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/admin-login")
def admin_login(admin: UserLogin):
    try:
        token = login_admin(admin)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
def logout(request: Request, 
           session_id: Optional[str] = Form(None), 
           token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    jti = payload.get("jti")
    exp = datetime.fromtimestamp(payload.get("exp"))
    if jti:
        blacklist_collection.insert_one({"jti": jti, "exp": exp})

        if session_id is not None:
            result = users_docs_collection.delete_many({"session_id": session_id})

        return {"detail": "✅ Successfully logged out."}
    else:
        raise HTTPException(status_code=400, detail="Invalid token format")
