from app.db.mongo import users_collection, admins_collection
from app.auth.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.models.user import UserCreate, UserLogin

def register_user(user: UserCreate):
    if users_collection.find_one({"username": user.username}):
        raise Exception("User already exists")

    hashed = hash_password(user.password)
    token = create_access_token({"sub": user.username, "role": "user"})

    users_collection.insert_one({
        "username": user.username,
        "hashed_password": hashed,
        "role": "user",
        "token": token
    })

    return token

def login_user(user: UserLogin):
    db_user = users_collection.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise Exception("Invalid credentials")

    token = create_access_token({"sub": user.username, "role": "user"})
    users_collection.update_one({"username": user.username}, {"$set": {"token": token}})
    return token

def login_admin(user: UserLogin):
    db_admin = admins_collection.find_one({"username": user.username})
    if not db_admin or not verify_password(user.password, db_admin["hashed_password"]):
        raise Exception("Invalid admin credentials")

    token = create_access_token({"sub": user.username, "role": "admin"})
    admins_collection.update_one({"username": user.username}, {"$set": {"token": token}})
    return token
