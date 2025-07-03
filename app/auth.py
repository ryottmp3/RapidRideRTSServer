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
- Passlib for secure password hashing.
- Python-JOSE for JWT encoding & decoding.
- Pydantic for request/response validation.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from database import get_db
from models import User

# Load environment variables from .env file
load_dotenv()

# JWT configuration - keep your secret key safe!
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing configuration using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 scheme for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

router = APIRouter(
    prefix="",
    tags=["authentication"],
    responses={404: {"description": "Not found"}}
)

# === Pydantic Schemas ===

class UserCreate(BaseModel):
    """
    Data required to register a new user.
    """
    username: str
    email: Optional[str] = None
    password: str

class Token(BaseModel):
    """Response model for access token."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data stored in JWT token payload."""
    username: Optional[str] = None

class UserInDB(BaseModel):
    """User metadata returned by protected endpoints."""
    id: int
    username: str
    email: Optional[str] = None

# === Utility Functions ===

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if provided password matches stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plaintext password for secure storage."""
    return pwd_context.hash(password)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Fetch a user record by username."""
    result = await db.execute(select(User).filter_by(username=username))
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Verify username and password combination.
    Returns user if successful, False otherwise.
    """
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generate a JWT token containing `sub` and expiration claims.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === API Endpoints ===

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    - Hashes the password.
    - Saves user to the database.
    - Returns an access token for immediate authentication.
    """
    # Check for existing username
    existing = await get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password and create user record
    hashed_pwd = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Issue JWT token
    access_token = create_access_token({"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 password flow endpoint.
    - Validates user credentials.
    - Returns a JWT access token if successful.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserInDB)
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user's metadata.
    - Decodes JWT token.
    - Retrieves user from database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception

    return UserInDB(id=user.id, username=user.username, email=user.email)

