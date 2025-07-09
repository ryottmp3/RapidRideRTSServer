# RapidRide Ticketing Server

This is the backend API server for the RapidRide transit fare system, designed to provide secure, low-cost digital ticketing infrastructure using cryptographically signed QR codes and Stripe-based payments.

---

## 🚍 Overview

RapidRide enables riders to purchase, store, and validate fare tickets through a secure FastAPI-based backend and a mobile-friendly frontend client. All tickets are digitally signed using Ed25519 to prevent forgery and duplication.

---

## 🛠️ Technology Stack

- **FastAPI** — high-performance Python web framework
- **ED25519** — cryptographic signing for tickets
- **PostgreSQL** or **SQLite** — ticket and user data
- **SQLAlchemy (async)** — database ORM
- **Stripe** — payment processing
- **Docker** (optional) — containerized deployment

---

## 🚧 Completed Milestones ✅

- [x] Ticket generation using ED25519 signatures
- [x] QR payload structure + base64 encoding
- [x] FastAPI backend with async validation
- [x] Stripe integration for payments
- [x] Wallet endpoint for ticket retrieval
- [x] Ticket validation via QR scan (`/validate`)
- [x] Ticket validation via ticket ID (`/check-ticket`)
- [x] Auth system with `/register` and `/token` endpoints
- [x] `.env`-based key and Stripe configuration
- [x] Secure API routing and session-based user context

---

## 🎯 Upcoming Milestones 🔜

- [ ] Admin dashboard (route usage, ticket stats, user mgmt)
- [ ] Stripe webhook logging + fraud detection
- [ ] Ticket expiration window and time-based validation
- [ ] Ticket type customization (multi-ride, day pass, etc.)
- [ ] JWT refresh + session invalidation
- [ ] Rate limiting and abuse protection
- [ ] Full Docker deployment with HTTPS reverse proxy
- [ ] OpenAPI documentation cleanup and security tags

---

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/yourname/rapidride-server.git
cd rapidride-server
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add a `.env` file:

```dotenv
ED25519_PRIVATE_KEY_B64=...
ED25519_PUBLIC_KEY_B64=...
STRIPE_PRIVATE_API_KEY=...
STRIPE_WEBHOOK_SECRET=...
FRONTEND_URL=http://localhost:3000
```

5. Run the server:

```bash
uvicorn server.main:app --reload
```

---

## 📁 API Endpoints

- `POST /register` – user registration
- `POST /token` – JWT token auth
- `POST /generate` – generate signed ticket
- `POST /validate` – validate QR payload
- `POST /check-ticket` – validate by ticket_id
- `GET /wallet` – list all user tickets
- `POST /create-checkout-session` – Stripe Checkout link

See `/docs` or `/redoc` for full auto-generated API docs.

---

## 📜 License

This project is licensed under the **GNU General Public License v3 (GPL-3.0)**. You are free to use, study, and modify the code, but redistribution must remain open-source under the same license.

---

## 👤 Author

Built by a solo developer as a civic infrastructure project for cities like Rapid City, SD.  
Contact: harley.glayzer@mines.sdsmt.edu

