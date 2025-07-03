# main.py

"""
RTS RapidRide Server
=====================
This FastAPI server exposes secure endpoints for:
    - Generating ED25519-signed fare tickets as base64 QR payloads.
    - Validating signed tickets via digital signature and database records.

Ticket generation is handled by the TicketGenerator class.
Ticket validation is handled by the TicketValidator class.

Requires a `.env` file with ED25519 key material:
    ED25519_PRIVATE_KEY_B64=...
    ED25519_PUBLIC_KEY_B64=...

Run:
    uvicorn main:app --reload
"""

import os
import base64
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from auth import router as auth_router
from auth import read_users_me

# Ticket crypto and DB handling
from ticketing import TicketGenerator, TicketValidator
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey
)

# Load key material from .env
load_dotenv()
priv_key_b64 = os.getenv("ED25519_PRIVATE_KEY_B64")
pub_key_b64 = os.getenv("ED25519_PUBLIC_KEY_B64")

if not priv_key_b64 or not pub_key_b64:
    raise RuntimeError("ED25519 keypair not found in .env")

# Decode from base64
priv_key_bytes = base64.b64decode(priv_key_b64)
pub_key_bytes = base64.b64decode(pub_key_b64)

# Initialize signer and verifier
ticket_generator = TicketGenerator(priv_key_bytes)
ticket_validator = TicketValidator(pub_key_bytes)

# FastAPI app
app = FastAPI(
    title="RTS Ticketing Server",
    description="Backend for generating and validating signed fare tickets.",
    version="1.0.0"
)

# Mount the auth endpoints
app.include_router(auth_router)
#   This registers:
#       POST /register
#       POST /token
#       GET /users/me

# ==== API SCHEMAS ====

class TicketRequest(BaseModel):
    """Data sent by client to request a ticket"""
    ticket_type: str = "single_use"
    valid_for: str | None = None  # Optional string like "2025-08"

class TicketValidationRequest(BaseModel):
    """Data sent by validator (scanner app) to verify a ticket"""
    payload_b64: str


# ==== ROUTES ====

@app.post("/generate", summary="Generate signed ticket", response_model=dict)
async def generate_ticket(
    data: TicketRequest,
    current_user = Depends(read_users_me)
):
    """
    Generates a digitally signed ticket for the given user.

    Returns a base64-encoded string suitable for QR code display.

    Request body:
        {
            "user_id": "abc123",
            "ticket_type": "single_use" | "monthly_pass",
            "valid_for": "2025-08"  # Optional for monthly_pass
        }

    Response:
        {
            "payload": "<base64-encoded ticket>"
        }
    """
    try:
        payload = await ticket_generator.generate_ticket(
            uid=current_user.id,
            ticket_type=data.ticket_type,
            valid_for=data.valid_for
        )
        return {"payload": payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticket generation failed: {e}")


@app.post("/validate", summary="Validate signed ticket", response_model=dict)
async def validate_ticket(data: TicketValidationRequest):
    """
    Verifies the cryptographic signature, issuer, and validity of a ticket payload.

    Used by fare enforcement tools (e.g., QR scanners) to verify ticket status.

    Request body:
        {
            "payload_b64": "<base64-encoded ticket+signature>"
        }

    Response:
        {
            "valid": true/false,
            "ticket_id": "...",
            "user_id": "...",
            "ticket_type": "...",
            "reason": "..."    # present only if invalid
        }
    """
    try:
        result = await ticket_validator.validate(data.payload_b64)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")

