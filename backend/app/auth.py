import os

from jose import jwt

SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

FAKE_USER = {
    "username": "admin",
"password": "admin123",
}


def login_user(username, password):
    normalized_username = username.strip()
    if (
        normalized_username == FAKE_USER["username"]
        and password == FAKE_USER["password"]
    ):
        token = jwt.encode({"user": normalized_username}, SECRET, algorithm=ALGORITHM)
        return {"token": token}
    return {"error": "Invalid credentials"}
