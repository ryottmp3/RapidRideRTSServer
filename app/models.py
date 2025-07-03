from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tickets = relationship("Ticket", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    stripe_price_id = Column(String(128), nullable=False, unique=True)
    stripe_product_id = Column(String(128), nullable=False, unique=True)
    duration_minutes = Column(Integer, default=90)
    active = Column(Boolean, default=True)

    tickets = relationship("Ticket", back_populates="product")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    ticket_code = Column(String(64), unique=True, nullable=False, index=True)  # QR code content
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    validated = Column(Boolean, default=False)

    user = relationship("User", back_populates="tickets")
    product = relationship("Product", back_populates="tickets")

