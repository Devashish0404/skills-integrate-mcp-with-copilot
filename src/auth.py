"""
Authentication and authorization utilities for the High School Management System.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum
import json
from pathlib import Path
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import hashlib
import hmac

# Security scheme
security = HTTPBearer()

# Role enumeration
class UserRole(str, Enum):
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"


# In-memory session storage (user -> token info)
sessions: Dict[str, Dict] = {}

# JWT token secret (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


class User:
    """User model with credentials and role"""
    def __init__(self, username: str, role: UserRole, active: bool = True):
        self.username = username
        self.role = role
        self.active = active


def load_credentials() -> Dict[str, Dict]:
    """Load user credentials from JSON file"""
    creds_file = Path(__file__).parent / "credentials.json"
    if not creds_file.exists():
        return {}
    with open(creds_file, "r") as f:
        return json.load(f)


def verify_password(stored_hash: str, password: str, salt: str) -> bool:
    """Verify password with salt"""
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return hmac.compare_digest(pwd_hash.hex(), stored_hash)


def create_simple_token(username: str) -> str:
    """Create a simple token for the session"""
    token = f"{username}:{datetime.utcnow().isoformat()}"
    sessions[token] = {
        "username": username,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return token


def get_current_user(credentials = Depends(security)) -> Dict:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    if token not in sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    session = sessions[token]
    
    if datetime.utcnow() > session["expires_at"]:
        del sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    
    credentials_data = load_credentials()
    username = session["username"]
    
    if username not in credentials_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user_data = credentials_data[username]
    if not user_data.get("active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    return {
        "username": username,
        "role": UserRole(user_data["role"]),
        "token": token
    }


def get_current_staff_or_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Dependency to ensure user is staff or admin"""
    if current_user["role"] not in [UserRole.STAFF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff and admin users can access this resource"
        )
    return current_user


def get_current_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Dependency to ensure user is admin"""
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this resource"
        )
    return current_user
