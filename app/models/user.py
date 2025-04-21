from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    role: str = "user"  # or "admin"
    token: str = ""
