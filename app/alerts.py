from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database import get_db
from models import User, Alert
from jose import jwt, JWTError
import os
from datetime import datetime

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_SECRET")
ALGORITHM = "HS256"

router = APIRouter(prefix="/alerts", tags=["alerts"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Pydantic Schemas
class AlertRequest(BaseModel):
    message: str

class AlertResponse(BaseModel):
    id: int
    message: str
    issued_at: str
    issued_by: str

# Auth helper
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    result = await db.execute(select(User).filter_by(username=username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# POST /alerts
@router.post("", status_code=200)
async def post_alert(
    alert: AlertRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can issue alerts.")

    new_alert = Alert(message=alert.message, issued_by=user.id)
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)
    return {"detail": "Alert sent.", "alert_id": new_alert.id}

# GET /alerts
@router.get("", response_model=list[AlertResponse])
async def get_alerts(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Alert).order_by(Alert.issued_at.desc()))
    alerts = result.scalars().all()
    return [
        AlertResponse(
            id=a.id,
            message=a.message,
            issued_at=a.issued_at.isoformat(),
            issued_by=a.issuer.username if a.issuer else "unknown"
        )
        for a in alerts
    ]

# DELETE /alerts/{alert_id}
@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete alerts.")

    result = await db.execute(select(Alert).filter_by(id=alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    await db.execute(delete(Alert).where(Alert.id == alert_id))
    await db.commit()
    return

