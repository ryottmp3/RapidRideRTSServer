# Main Server Code

import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

app = FastAPI()

# CORS (for localhost development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Create Checkout Session ---
@app.post("/api/create-checkout-session")
async def create_checkout(data: dict):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': data['price_id'],  # lookup by ticket type
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('DOMAIN_URL')}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('DOMAIN_URL')}/cancel",
            metadata={
                'user_id': data['user_id'],
                'ticket_type_id': data['ticket_type_id']
            }
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Stripe Webhook ---
@app.post("/api/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig, webhook_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        ticket_type = session["metadata"]["ticket_type_id"]

        # Generate ticket (insert QR, expiry, etc.)
        generate_and_store_ticket(user_id, ticket_type)

    return {"status": "ok"}

def generate_and_store_ticket(user_id, ticket_type_id):
    ticket_id = f"RR-{user_id}-{ticket_type_id}-{os.urandom(4).hex()}"
    # Save to SQLite (client wallet) and Postgres/SQLite (server verification DB)
    print(f"Generated ticket {ticket_id} for user {user_id}, type {ticket_type_id}")
    # TODO: Save in database

