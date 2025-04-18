from fastapi import APIRouter, Form

auth_router = APIRouter()

# Dev token endpoint for Swagger to work
@auth_router.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    # Ignore username/password — return the dev token
    return {"access_token": "secret123", "token_type": "bearer"}


# def create_token(username: str, role: str = "user"):
#     payload = {
#         "sub": username,
#         "role": role,
#         "exp": datetime.utcnow() + timedelta(minutes=60)
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
