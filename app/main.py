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
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
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

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rts.server.main")

# Load key material from .env
load_dotenv("../.env")
priv_key_b64 = os.getenv("ED25519_PRIVATE_KEY_B64")
pub_key_b64 = os.getenv("ED25519_PUBLIC_KEY_B64")

if not priv_key_b64 or not pub_key_b64:
    logger.error("ED25519 Keypair not found in .env")
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

# ==== Public Key endpoint for client-side validation ====
@app.get("/public_key", summary="Get ED25519 Pubkey")
async def public_key_endpoint():
    """Returns new raw ED25519 public key bytes in DER format"""
    logger.debug(f"Serving ED25519 Pubkey, {len(pub_key_bytes)} bytes")
    return Response(content=pub_key_bytes, media_type="application/octet-stream")

# ==== NEW: Stripe sandbox integration ====
import stripe
from fastapi import Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

class PaymentRequest(BaseModel):
    """Data for creating a Stripe PaymentIntent"""
    amount: int
    currency: str = "usd"

@app.post("/create-payment-intent", summary="Create Stripe PaymentIntent")
async def create_payment_intent(
    data: PaymentRequest,
    current_user = Depends(read_users_me)
):
    try:
        intent = stripe.PaymentIntent.create(
            amount=data.amount,
            currency=data.currency,
            metadata={"user_id": str(current_user.id)}
        )
        logger.debug("Created PaymentIntent %s for user %s", intent.id, current_user.username)
        return {"client_secret": intent.client_secret}
    except Exception as e:
        logger.error("Failed to create PaymentIntent: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stripe-webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        logger.debug("Received Stripe event: %s", event["type"])
    except stripe.error.SignatureVerificationError as e:
        logger.error("Webhook signature verification failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle payment events
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        logger.info("PaymentIntent succeeded: %s", intent["id"])
        # TODO: fulfill order or record success
    else:
        logger.info("Unhandled Stripe event type: %s", event["type"])

    return {"status": "success"}

# ==== ROUTES ====

# ==== Stripe Checkout Session creation ====
import stripe
from fastapi import Request

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

class CheckoutRequest(BaseModel):
    ticket_type: str = "single_use"
    valid_for: str | None = None

@app.post("/create-checkout-session", summary="Create Stripe Checkout Session")
async def create_checkout_session(
    data: CheckoutRequest,
    current_user = Depends(read_users_me)
):
    """
    Creates a Stripe Checkout Session for the given ticket type.
    Returns a URL for the client to redirect to.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Ticket: {data.ticket_type}"},
                    "unit_amount": 500,  # placeholder amount in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{FRONTEND_URL}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/payment-cancel",
            metadata={
                "user_id": str(current_user.id),
                "ticket_type": data.ticket_type,
                **({"valid_for": data.valid_for} if data.valid_for else {})
            }
        )
        logger.debug("Created Stripe Checkout Session %s for user %s", session.id, current_user.username)
        return {"url": session.url}
    except Exception as e:
        logger.error("Failed to create Checkout Session: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

# ==== Webhook to fulfill order ==== ====
@app.post("/stripe-webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        logger.debug("Received Stripe event: %s", event.type)
    except Exception as e:
        logger.error("Webhook signature verification failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        ticket_type = session.metadata.get("ticket_type")
        valid_for = session.metadata.get("valid_for")
        try:
            # generate and persist ticket
            payload = await ticket_generator.generate_ticket(
                uid=int(user_id),
                ticket_type=ticket_type,
                valid_for=valid_for
            )
            logger.info("Generated ticket for user %s after payment", user_id)
        except Exception as e:
            logger.error("Error generating ticket after payment: %s", e)
    else:
        logger.info("Unhandled Stripe event type: %s", event.type)

    return {"status": "success"}

# ==== Wallet retrieval endpoint ====
class TicketModel(BaseModel):
    ticket_id: str
    payload: str
    ticket_type: str

@app.get("/wallet", summary="List user tickets", response_model=list[TicketModel])
async def get_wallet(current_user = Depends(read_users_me)):
    """
    Returns all tickets generated for the current user.
    """
    try:
        records = await ticket_validator.list_tickets_for_user(current_user.id)
        result = [
            TicketModel(ticket_id=str(r.id), payload=r.payload, ticket_type=r.ticket_type)
            for r in records
        ]
        logger.debug("Retrieved %d tickets for user %s", len(result), current_user.username)
        return result
    except Exception as e:
        logger.error("Error retrieving wallet: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


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
        logger.debug(f"Generated ticket payload for user {current_user.username}")
        return {"payload": payload}
    except Exception as e:
        logger.error(f"Ticket Generation failed: {e}")
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
        logger.debug(f"Ticket Validation Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Validation Error: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {e}")

