# Database

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    product = Column(String, primary_key=True)
    price = Column(String)
    payment_link = Column(String)

engine = create_engine("sqlite:///products.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
