# routes/validate.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Ticket  # Adjust if needed
import uuid
import logging

router = APIRouter()
logger = logging.getLogger("rts.server.validate")

class ValidationRequest(BaseModel):
    ticket_id: uuid.UUID

@router.post("/validate")
async def validate_ticket(
    request: ValidationRequest,
    session: AsyncSession = Depends(get_db)
):
    ticket_id = request.ticket_id
    logger.debug(f"Validating ticket_id: {ticket_id}")

    ticket = await session.get(Ticket, str(ticket_id))
    if not ticket:
        logger.info(f"Ticket not found: {ticket_id}")
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not ticket.status:
        logger.info(f"Ticket already used: {ticket_id}")
        return {"status": "already_used"}

    return {"status": "valid"}

