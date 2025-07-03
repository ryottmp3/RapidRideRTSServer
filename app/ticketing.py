# Ticketing

import base64
import argparse
import sys
import uuid
import os
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from dotenv import load_dotenv
from pathlib import Path
from ticketdb import Ticket, Session


def initialize_signing_key():
    print("Initialization Protocol: Generating Private ED25519 Key... \n")
    private_key = Ed25519PrivateKey.generate()
    key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    pubkey_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    pubkey_b64 = base64.b64encode(pubkey_bytes).decode()
    key_b64 = base64.b64encode(key_bytes).decode()
    # pubhash = hashlib.sha256(pubkey_bytes).hexdigest()
    # print(f"Public Key Hash: {pubhash}")

    env_file = Path("../.env")
    existing_lines = []
    if env_file.exists():
        existing_lines = env_file.read_text().splitlines()
        existing_lines = [
            line for line in existing_lines if not line.startswith(
                ("ED25519_PRIVATE_KEY_B64=", "ED25519_PUBLIC_KEY_B64")
            )
        ]

    existing_lines.append(f"ED25519_PRIVATE_KEY_B64={key_b64}")
    existing_lines.append(f"ED25519_PUBLIC_KEY_B64={pubkey_b64}")
    try:
        env_file.write_text("\n".join(existing_lines) + "\n")
        print(f"Wrote new ED25519 Private & Public Keys to {env_file}")
    except Exception as e:
        raise RuntimeError(f"Failed to write to .env: {e}")

    derived_pub = Ed25519PrivateKey.from_private_bytes(
        key_bytes
    ).public_key()
    assert derived_pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ) == pubkey_bytes, "Public key doesn't match private key"

    sys.exit(0)


class TicketGenerator:
    def __init__(
        self,
        private_key_bytes: bytes,
        issuer: str = "RTS RapidRide"
    ):
        self.private_key = Ed25519PrivateKey.from_private_bytes(
            private_key_bytes
        )
        self.issuer = issuer

    def generate_ticket(
        self,
        uid: str,
        ticket_type: str = "single_use",
        valid_for=None
    ) -> dict:
        now = datetime.now(ZoneInfo("America/Denver"))
        ticket = {
            "ticket_id": str(uuid.uuid4()),
            "user_id": uid,
            "ticket_type": ticket_type,
            "valid_for": str(valid_for),
            "issued_at": now.strftime("%Y%m%d_%H%M%z"),
            "issuer": self.issuer
        }
        signature = self.sign_ticket(ticket)
        self.save_ticket(ticket, signature)
        QRP = self.create_QR_payload(ticket, signature)
        return QRP

    def serialize_ticket(
        self,
        ticket: dict
    ) -> str:
        """Canonical JSON format -- sorted keys, no whitespace"""
        return json.dumps(ticket, separators=(',', ':'), sort_keys=True)

    def sign_ticket(
        self,
        ticket: dict
    ) -> str:
        ticket_json = self.serialize_ticket(ticket).encode()
        # ticket_hash = hashlib.sha256(ticket_json).hexdigest()
        # print(f"[GENERATOR] SHA256(ticket_json): {ticket_hash}")
        signature = self.private_key.sign(ticket_json)

        return base64.b64encode(signature).decode()

    def create_QR_payload(
        self,
        ticket: dict,
        signature: str
    ) -> str:
        """Combine ticket and signature into a payload"""
        # pubkey_bytes = self.private_key.public_key().public_bytes(
        #     encoding=serialization.Encoding.Raw,
        #     format=serialization.PublicFormat.Raw
        # )
        # pubkey_b64 = base64.b64encode(pubkey_bytes).decode()

        signed_ticket = {
            "ticket": ticket,
            "signature": signature,
            # "public_key": pubkey_b64
        }

        QR_Payload = base64.b64encode(
            json.dumps(signed_ticket).encode()
        ).decode()
        return QR_Payload

    def save_ticket(
        self,
        ticket: dict,
        signature: str
    ):
        """Calls the Database API to save a ticket to a uid"""
        session = Session()
        db_ticket = Ticket(
            ticket_id=ticket["ticket_id"],
            user_id=ticket["user_id"],
            ticket_type=ticket["ticket_type"],
            valid_for=ticket.get("valid_for"),
            issued_at=ticket["issued_at"],
            issuer=ticket["issuer"],
            signature=signature
        )
        session.add(db_ticket)
        session.commit()
        session.close()


class TicketValidator:
    def __init__(
        self,
        pubkey_bytes: bytes,
        trusted_issuer: str = "RTS RapidRide",
        timezone: str = "America/Denver"
    ):
        self.pubkey = Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        self.trusted_issuer = trusted_issuer
        self.tz = ZoneInfo(timezone)

    def decode_payload(
        self,
        payload_b64: str
    ) -> dict:
        try:
            payload_json = base64.b64decode(payload_b64).decode()
            # print(f"Validation Payload: {payload_json}")
            return json.loads(payload_json)
        except Exception as e:
            raise ValueError(f"Invalid QR Payload: {e}")

    def serialize_ticket(
        self,
        ticket: dict
    ) -> str:
        return json.dumps(ticket, separators=(',', ':'), sort_keys=True)

    def verify_signature(
        self,
        ticket: dict,
        signature_b64: str
    ) -> bool:
        try:
            signature = base64.b64decode(signature_b64)
            ticket_json = self.serialize_ticket(ticket).encode()
            # ticket_hash = hashlib.sha256(ticket_json).hexdigest()
            # print(f"[VALIDATOR] SHA256(ticket_json): {ticket_hash}")
            self.pubkey.verify(signature, ticket_json)
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            print(e)
            return False

    def is_ticket_valid_now(
        self,
        ticket: dict
    ) -> bool:
        ticket_type = ticket.get("ticket_type")
        valid_for = ticket.get("valid_for")
        now = datetime.now(self.tz)

        if ticket_type == "single_use":
            return True

        elif ticket_type == "monthly_pass":
            try:
                yr_mo = datetime.strptime(valid_for, "%Y-%m")
                return yr_mo.year == now.year and yr_mo.month == now.month
            except Exception as e:
                print(e)
                return False

        return False  # Unknown or malformed ticket

    def get_ticket_by_id(
        self,
        ticket_id: str
    ) -> Ticket | None:
        session = Session()
        ticket = session.query(Ticket).filter_by(ticket_id=ticket_id).first()
        return ticket

    def validate(
        self,
        payload_b64: str
    ) -> dict:
        try:
            payload = self.decode_payload(payload_b64)
            ticket = payload["ticket"]
            signature = payload["signature"]
            db_record = self.get_ticket_by_id(ticket["ticket_id"])

            # This code is for embedded public keys;
            # Low-Security Option
            #
            # embedded_pubkey_b64 = payload["public_key"]
            #
            # embedded_pubkey = Ed25519PublicKey.from_public_bytes(
            #     base64.b64decode(embedded_pubkey_b64)
            # )
            #
            # ticket_json = self.serialize_ticket(ticket).encode()
            # signature_bytes = base64.b64decode(signature)
            #
            # embedded_pubkey.verify(signature_bytes, ticket_json)

            if ticket.get("issuer") != self.trusted_issuer:
                return {
                    "valid": False,
                    "reason": f"Issuer mismatch: expected '{
                        self.trusted_issuer
                    }'"
                }

            if not self.verify_signature(ticket, signature):
                return {
                    "valid": False,
                    "reason": "Invalid digital signature"
                }

            if not self.is_ticket_valid_now(ticket):
                return {
                    "valid": False,
                    "reason": "Ticket not valid for current time"
                }


            if not db_record:
                return {
                    "valid": False,
                    "reason": "Ticket does not exist in database."
                }

            if db_record.status != "active":
                return {
                    "valid": False,
                    "reason": f"Ticket status: {db_record.status}"
                }

            return {
                "valid": True,
                "ticket_id": ticket["ticket_id"],
                "user_id": ticket["user_id"],
                "ticket_type": ticket["ticket_type"]
            }
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Validation error: {e}"
            }
        """
        except InvalidSignature:
            return {
                "valid": False,
                "reason": "Invalid Digital Signature"
            }
        """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RTS Ticketing System")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize the ed25519 and exit."
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate several different ticket types"
    )

    args = parser.parse_args()

    if args.init:
        initialize_signing_key()

    # Initialize Environment Variables
    load_dotenv("../.env")
    priv_key_b64 = os.getenv("ED25519_PRIVATE_KEY_B64")
    priv_bytes = base64.b64decode(priv_key_b64)
    private_key = Ed25519PrivateKey.from_private_bytes(priv_bytes)
    pub_key_b64 = os.getenv("ED25519_PUBLIC_KEY_B64")
    pub_bytes = base64.b64decode(pub_key_b64)
    pubhash = hashlib.sha256(pub_bytes).hexdigest()
    # print(f"Public Key Hash: {pubhash}")

    # print(repr(os.getenv("ED25519_PRIVATE_KEY_B64")))
    derived_pub = Ed25519PrivateKey.from_private_bytes(
        priv_bytes
    ).public_key()
    assert derived_pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ) == pub_bytes, "Public key doesn't match private key"
    if args.generate:
        gen = TicketGenerator(priv_bytes)
        t1 = gen.generate_ticket(uid="001132")
        t2 = gen.generate_ticket(
            uid="001131",
            ticket_type="monthly_pass",
            valid_for="2025-08"

        )
        check = TicketValidator(pub_bytes)
        v1 = check.validate(t1)
        v2 = check.validate(t2)

        print(f"Q1 Validation: {v1}")
        print(f"Q2 Validation: {v2}")
