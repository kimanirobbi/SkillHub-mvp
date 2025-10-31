import requests, os

def stk_push(phone, amount):
    access_token = os.getenv("MPESA_ACCESS_TOKEN")
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    payload = {
        "BusinessShortCode": os.getenv("MPESA_SHORTCODE"),
        "Password": os.getenv("MPESA_PASSWORD"),
        "Timestamp": "20251015120000",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": os.getenv("MPESA_SHORTCODE"),
        "PhoneNumber": phone,
        "CallBackURL": os.getenv("MPESA_CALLBACK_URL"),
        "AccountReference": "SkillHub",
        "TransactionDesc": "SkillHub Service Payment"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.post(url, json=payload, headers=headers).json()
