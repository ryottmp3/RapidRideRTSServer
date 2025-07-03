# Database

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(String, primary_key=True)
    user_id = Column(String)
    ticket_type = Column(String)
    valid_for = Column(String)
    issued_at = Column(String)
    issuer = Column(String)
    signature = Column(Text)
    status = Column(String, default="active")

engine = create_engine("sqlite:///tickets.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
