# 🚍 RapidRide Mobile Ticketing App

A lightweight, cost-effective mobile and web-based app for the **Rapid City RTS RapidRide** transit system.
This app enables users to:

- View fixed bus schedules (no real-time tracking)
- Purchase and store digital bus tickets
- Display QR codes to be scanned for boarding
- Receive admin-posted alerts for delays and cancellations

---

## Requirements

<bold>Arch Linux Packages<\bold>
 - pyside6
 - pyside6-tools
 - python-segno (AUR)
 - python-qrcode-artistic (AUR)
   - yay -S python-segno python-qrcode-artistic --mflags --nocheck 
 - python-dotenv
 - sqlite
 - python-sqlalchemy
 - postgresql
   - sudo su -l postgres -c "initdb --locale=C.UTF-8 --encoding=UTF8 -D '/var/lib/postgres/data'"
   - sudo systemctl enable --now postgresql
   - sudo -u postgres psql
     - CREATE ROLE rts WITH LOGIN PASSWORD 'rapidride';
     - CREATE DATABASE rapidride_db OWNER rts;
     - ALTER ROLE rts CREATEDB;
     - \q

---

## 🛠 Tech Stack

| Component         | Stack                        |
|------------------|------------------------------|
| Frontend (Mobile)| Python (Kivy) or C++ (Qt)     |
| Backend API      | Python (FastAPI)              |
| Database         | Supabase (PostgreSQL)         |
| Ticket Validator | C++ with OpenCV + ZBar        |
| Admin Dashboard  | Flask or FastAPI + HTML       |
| Payments         | Stripe API                    |

---

## 💸 Ticket Types & Pricing

| Ticket Type       | Cash Price   | Card Price  | Details                             |
|-------------------|--------------|-------------|-------------------------------------|
| Single Ride       | $1.50        | $1.85       | Purchase on bus only                |
| 10-Ride Pass      | $13.50       | $14.25      | 10 single rides; track remaining    |
| Monthly Pass      | $30.00       | $31.25      | Unlimited rides for 30 days         |


---

## 📋 Project Roadmap

A checklist-style development roadmap broken into **four core phases**.
The initial version does not include real-time GPS, maps, or live bus tracking.

---

## ✅ Phase I: Static Schedule Viewer

🕐 Display posted schedules from GTFS or CSV.

### Tasks:
- <strike> [ ] Download or convert RapidRide's schedule to GTFS or structured CSV </strike>
- <strike> [ ] Parse `routes.txt`, `stops.txt`, `stop_times.txt`, `trips.txt` </strike>
  - Routes are viewed via PDF file, map-based routes/schedules will be implemented later on.
- [x] Build mobile app UI to:
  - [x] Browse by route
  - [x] Show stop times for each route/day
- [ ] Include section for admin-posted alerts

---

## 🎟 Phase II: Ticket Purchase & QR Code Generator

🛒 Generate QR tickets via backend API after Stripe payment.

### Tasks:
- [ ] Build `/buy_ticket` FastAPI endpoint
- [x] Support all ticket types (single, 10-ride, monthly)
- [x] Generate QR code using UUID + expiration metadata
- [ ] Store ticket in Supabase with status tracking
- [ ] Display ticket in mobile app (including expiration countdown)

---

## 🛠 Phase III: Admin Dashboard & Ticket Validator

🧰 Allow drivers or staff to scan QR tickets and post alerts.

### Ticket Validator (C++):
- [ ] Scan QR using OpenCV + ZBar
- [ ] Send UUID to backend `/validate_ticket` endpoint
- [ ] Backend checks:
  - [ ] Valid?
  - [ ] Expired?
  - [ ] Already used?

### Admin Dashboard:
- [ ] Web UI (Flask/FastAPI + simple HTML)
- [ ] Admin login
- [ ] Post service alerts by route or date
- [ ] View ticket usage logs

---

## 📍 Phase IV: Nearby Stops via GPS (Future Feature)

🗺️ Use phone location to show nearest stops and upcoming scheduled buses (no real-time tracking).

### Tasks:
- [ ] Use phone GPS (via `plyer` or `geopy`)
- [ ] Parse `stops.txt` for coordinates
- [ ] Calculate nearest stops using Haversine distance
- [ ] Show upcoming departures using `stop_times.txt` data

---

## 🧱 Optional Features

- [ ] Prepaid ticket codes (offline payment compatibility)
- [ ] Ticket gifting (send a ride to someone else)
- [ ] Kiosk mode (install app on public devices)

---

## 🔐 Security Notes

- Tickets use UUID stored in backend
- QR codes expire or decrement ride count on scan
- Prevent re-use by marking as scanned
- (Optional) Add encryption (e.g., JWT) in later versions

---

## 💰 Cost Estimate

| Resource          | Cost Estimate       |
|-------------------|---------------------|
| Hosting (Render/Railway) | $0–$7/month    |
| Supabase (DB/Auth) | Free tier covers MVP |
| Stripe Fees        | 2.9% + $0.30/txn    |
| Domain Name        | ~$12/year (optional) |
| Ticket Validator   | Open-source; no cost |
| Dev Tools          | Free (Python/C++)   |

---

## 🧭 Deployment Checklist

**Minimum Viable Product (MVP):**
- [ ] Routes & schedules display correctly
- [ ] Stripe payment and ticket generation work
- [ ] Admin dashboard can post alerts
- [ ] QR scanner works and verifies ticket status

**Phase IV Readiness:**
- [ ] Phone GPS accessible
- [ ] Stops are accurately geo-located
- [ ] List of nearby stops with schedules is functional

---

## ✨ License

This project is intended for public service use. All code will be released under the [MIT License](https://opensource.org/licenses/MIT) unless otherwise specified.

---

## 📬 Contact

Want to collaborate with the RapidRide transit agency?
Reach out to their official site: [https://www.rcgov.org/departments/public-works/transit-division-rts.html](https://www.rcgov.org/departments/public-works/transit-division-rts.html)
