# app/auth.py
"""
Authentication and authorization module for RTS RapidRide Server.

This module provides:
- User registration with password hashing (bcrypt).
- Token-based authentication (JWT) for secure endpoints.
- Utility functions for hashing and verifying passwords.
- OAuth2 password flow endpoints:
    - POST /register to create a new user account.
    - POST /token to obtain an access token.
    - GET /users/me to retrieve current user metadata.

Dependencies:
- FastAPI for web framework.
- SQLAlchemy async session for database operations.
- python-bcrypt for secure password hashing.
- Python-JOSE for JWT encoding & decoding.
- Pydantic for request/response validation.
- Python logging for debug tracing.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from database import get_db
from models import User
from models import RefreshToken as DBRefreshToken

# Load environment variables from .env file
load_dotenv()

# Configure logger for this module
logger = logging.getLogger("rts.auth")
# If running under uvicorn with --log-level debug or trace, these debug calls will be shown.

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

router = APIRouter(
    prefix="",
    tags=["authentication"],
    responses={404: {"description": "Not found"}}
)

# === Pydantic Schemas ===

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_admin: bool

# === Utility Functions with Debug Tracing ===


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt and return a UTF-8 string for storage."""
    logger.debug("Hashing password: <hidden> bytes length=%d", len(password))
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    hashed_str = hashed.decode("utf-8")
    logger.debug("Generated bcrypt hash: %s...", hashed_str[:29])
    return hashed_str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Returns True if `plain_password` matches the stored bcrypt hash."""
    logger.debug("Verifying password against hash: %s...", hashed_password[:29])
    pwd_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    result = bcrypt.checkpw(pwd_bytes, hashed_bytes)
    logger.debug("Password verification result: %s", result)
    return result

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    logger.debug("Fetching user by username: %s", username)
    result = await db.execute(select(User).filter_by(username=username))
    user = result.scalars().first()
    logger.debug("User fetched: %s", "found" if user else "not found")
    return user

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    logger.debug("Authenticating user: %s", username)
    user = await get_user_by_username(db, username)
    if not user:
        logger.debug("Authentication failed: user not found")
        return None
    if not verify_password(password, user.hashed_password):
        logger.debug("Authentication failed: invalid password")
        return None
    logger.debug("Authentication succeeded for user: %s", username)
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))  # 15 min
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=90)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# === API Endpoints with Debug Tracing ===

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    logger.debug("Register endpoint called for username: %s", user.username)
    existing = await get_user_by_username(db, user.username)
    if existing:
        logger.debug("Registration failed: username already exists: %s", user.username)
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pwd = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    logger.debug("Creating new user record: %s", user.username)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token({"sub": new_user.username})
    refresh_token = create_refresh_token({"sub": new_user.username})
    logger.debug("Registration successful, issuing token for user: %s", new_user.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    logger.debug("Token endpoint called for username: %s", form_data.username)
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.debug("Login failed for username: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    # Save Refresh Token in DB
    db_token = DBRefreshToken(token=refresh_token, user_id=user.id)
    db.add(db_token)
    await db.commit()
    logger.debug("Login successful, issuing token for user: %s", user.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/users/me", response_model=UserInDB)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    logger.debug("Users/me endpoint called with token: %s...", token[:20])
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.debug("JWT decode succeeded but no sub claim found")
            raise credentials_exception
        logger.debug("JWT decoded, subject: %s", username)
        token_data = TokenData(username=username)
    except JWTError as e:
        logger.debug("JWT decode error: %s", e)
        raise credentials_exception

    user = await get_user_by_username(db, token_data.username)
    if user is None:
        logger.debug("User not found for subject in token: %s", token_data.username)
        raise credentials_exception

    logger.debug("Users/me returning data for user: %s", user.username)
    return UserInDB(
        id=user.id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin
    )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token: str = Depends(oauth2_scheme),  # Send refresh token in Authorization: Bearer ...
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Check token exists and not revoked
    result = await db.execute(select(DBRefreshToken).filter_by(token=token))
    db_token = result.scalar_one_or_none()
    if db_token is None or db_token.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token = create_access_token({"sub": username})
    return {"access_token": access_token, "refresh_token": token, "token_type": "bearer"}

