# Create Products with Stripe API

import os
import stripe
from dotenv import load_dotenv
from productdb import Session, Product


class ProductCreation:
    def __init__(self):
        pass

    def create_product(
        self,
        product_name: str,
        product_desc: str,
        product_price: int,
        product_currency: str = "usd",
    ):
        """Creates Stripe Product"""
        try:
            product = stripe.Product.create(
                name=product_name,
                description=product_desc
            )
            price = stripe.Price.create(
                unit_amount=product_price,
                currency=product_currency,
                product=product['id']
            )
            line_items = {
                "price": price['id'],
                "quantity": 1
            }
            payment_link = stripe.PaymentLink.create(
                line_items=[line_items],
            )
            new_product = {
                "product": product,
                "price": price,
                "payment_link": payment_link
            }
            self.save_product(new_product)
            return "Task Successful"
        except Exception as e:
            raise RuntimeError(f"Product Creation Unsuccessful: {e}")

    def save_product(
            self,
            product: dict
    ):
        session = Session()
        db_product = Product(
            product=product["product"]["id"],
            price=product["price"]["id"],
            payment_link=product["payment_link"]["url"]
        )
        session.add(db_product)
        session.commit()
        session.close()


if __name__ == "__main__":
    # Load environment Variables
    load_dotenv("../.env")
    stripe.api_key = os.getenv("STRIPE_PRIVATE_API_KEY")

    # Create Products
    prod = ProductCreation()
    prod.create_product(
        product_name="single_use",
        product_desc="Single Use Transit Fare",
        product_price=185
    )
    prod.create_product(
        product_name="ten_pack",
        product_desc="Ten Pack of Transit Fares",
        product_price=1425
    )
    prod.create_product(
        product_name="monthly_pass",
        product_desc="One Month Unlimited Transit Fares",
        product_price=3125
    )
