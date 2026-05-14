import requests
import os
from dotenv import load_dotenv

load_dotenv()

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")


def initialize_payment(email, amount):

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": int(amount * 100),
        "callback_url": "http://127.0.0.1:5000/success"
    }

    response = requests.post(
        url,
        json=data,
        headers=headers
    )

    return response.json()


def verify_payment(reference):

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}"
    }

    response = requests.get(
        url,
        headers=headers
    )

    return response.json()