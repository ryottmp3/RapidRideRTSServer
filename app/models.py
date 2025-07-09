from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    # Securely store the user's password hash for authentication
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)

    # One-to-many relationship: a user can have multiple tickets
    tickets = relationship("Ticket", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    stripe_price_id = Column(String(128), nullable=False, unique=True)
    stripe_product_id = Column(String(128), nullable=False, unique=True)
    active = Column(Boolean, default=True)

    # No tickets relationship since Ticket does not reference product_id


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(String, primary_key=True, unique=True, nullable=False)
    ticket_type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issued_at = Column(String)
    valid_for = Column(String)
    issuer = Column(String)
    signature = Column(String)
    status = Column(Boolean, default=True)
    ticket = Column(String)
    qr = Column(String)

    # Link back to the owning user
    user = relationship("User", back_populates="tickets")
    # Removed product relationship since no product_id column


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="refresh_tokens")
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    message = Column(String)
    issued_at = Column(DateTime, default=datetime.utcnow)
    issued_by = Column(Integer, ForeignKey("users.id"))
