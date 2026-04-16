"""
Authentication module for RAG application.

This module handles JWT token generation and user authentication.
For production use, integrate with a proper user database (PostgreSQL, MySQL, SQLite).

WARNING: DEMO_USER credentials are hardcoded for testing only. Replace with database-backed auth in production.
"""

import os
from jose import jwt

# JWT configuration
SECRET = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"

# Demo credentials - FOR TESTING ONLY
# In production: Query user credentials from database table users(username, hashed_password_hash)
DEMO_USER = {
    "username": "admin",
    "password": "admin123",
}


def login_user(username: str, password: str) -> dict:
    """
    Authenticate user and generate JWT token.
    
    Args:
        username (str): User login username
        password (str): User plaintext password (should be hashed in production)
    
    Returns:
        dict: Contains "token" on success, or "error" key on authentication failure
        
    Raises:
        None (returns dict with "error" key instead)
        
    Security Notes:
        - In production, fetch from database and use password hashing (bcrypt/argon2)
        - This demo uses plaintext comparison - INSECURE for production
        - Example production query: SELECT * FROM users WHERE username = ? AND password_hash = ?
    """
    # Normalize input: strip whitespace
    normalized_username = username.strip()
    
    # Validate credentials against demo user
    # TODO: Replace with database query when implementing production auth
    if (
        normalized_username == DEMO_USER["username"]
        and password == DEMO_USER["password"]
    ):
        # Generate JWT token with user info
        token = jwt.encode({"user": normalized_username}, SECRET, algorithm=ALGORITHM)
        return {"token": token}
    
    # Return error on failed authentication
    return {"error": "Invalid credentials"}
