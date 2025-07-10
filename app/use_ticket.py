# routes/validate.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Ticket  # Adjust if needed
import uuid
import logging

router = APIRouter()
logger = logging.getLogger("rts.server.use")

class UsageRequest(BaseModel):
    ticket_id: uuid.UUID

@router.post("/use-ticket")
async def use_ticket(
    request: UsageRequest,
    session: AsyncSession = Depends(get_db)
):
    ticket_id = request.ticket_id
    logger.debug(f"Invalidating ticket_id: {ticket_id}")

    ticket = await session.get(Ticket, str(ticket_id))
    if not ticket:
        logger.info(f"Ticket not found: {ticket_id}")
        raise HTTPException(status_code=404, detail="Ticket not found")

    if not ticket.status:
        logger.info(f"Ticket already used: {ticket_id}")
        return {"status": "already_used"}

    if ticket.ticket_type == "single_use":
        ticket.valid = False
        await session.commit()
        logger.info(f"Ticket {ticket_id} marked as used")

    return {"status": "valid"}

