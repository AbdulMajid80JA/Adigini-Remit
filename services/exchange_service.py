import requests

API_KEY = "03ee19a7d0808f0da0568c0e"

BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"


def get_exchange_rates():

    try:

        response = requests.get(BASE_URL)

        data = response.json()

        if data["result"] == "success":

            rates = data["conversion_rates"]

            return {
                "USD": rates.get("GHS"),
                "EUR": rates.get("EUR"),
                "GBP": rates.get("GBP"),
                "SAR": rates.get("SAR"),
                "AED": rates.get("AED"),
                "QAR": rates.get("QAR"),
                "KWD": rates.get("KWD"),
                "NGN": rates.get("NGN"),
                "XOF": rates.get("XOF")
            }

        return {}

    except Exception as e:
        print("Exchange API Error:", e)
        return {}