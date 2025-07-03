# Payment with Stripe API

import stripe
from productdb import Product, Session

class HandlePayment:
    def __init__(
        self,
        ticket_type: str
    ):
        """Initializes Payment Handler Class"""
        self.ticket_type = ticket_type

    def fetch_stripe_link(
        self,
        ticket_type: str
    ) -> str:
        """Fetches stripes link from database"""
        session = Session()
        product = session.query(Product).filter_by(product=ticket_type).first()
        return product.payment_link

    def open_payment
