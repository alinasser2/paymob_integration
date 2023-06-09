import requests
# from django.http import HttpResponse
import json
from django.conf import settings


class payment_gateway():
    _api_key = settings.PAYMOB_API_KEY
    _ENDPOINT: str = "https://accept.paymob.com/api"
    _TOKEN_URL: str = f"{_ENDPOINT}/auth/tokens"
    _ORDER_URL: str = f"{_ENDPOINT}/ecommerce/orders"
    _PAYMENT_KEY_URL: str = f"{_ENDPOINT}/acceptance/payment_keys"
    _IFRAME_ID: int = settings.PAYMOB_IFRAME_ID
    _INTEGRATION_ID: int = settings.PAYMOB_INTEGRATION_ID
    _PAY_URL: str = f"https://accept.paymob.com/api/acceptance/iframes/{_IFRAME_ID}"

    def __init__(self, total_price, request , country , items):
        self.total_price = total_price
        self.country = country
        self.billing_data = {
                "email": request.user.email ,
                "phone_number": request.user.phone,
                "country": "EGP",
                "city": request.user.customer_profile.city,
                "apartment": request.user.customer_profile.appartment,
                "floor": request.user.customer_profile.floor,
                "first_name": request.user.firstname,
                "last_name": request.user.lastname,
                "street": request.user.customer_profile.address,
                "building": request.user.customer_profile.appartment,
                "postal_code": request.user.customer_profile.postal_code,
                "state": request.user.customer_profile.city,
            }
        self.items = items
        
        


    def authentication_request(self) -> str:
        res = requests.post(self._TOKEN_URL,json = {
        "api_key" : self._api_key
        })
        res = res.json()
        token = res['token']
        return token
    

    def order_registration(self, token : str, items : list = [] , shipping_data : dict = {} , shipping_details : dict = {}) -> str:
        
        data = {
        "auth_token":  token,
        "delivery_needed": "false",
        "amount_cents": str(self.total_price),
        "currency": "EGP",
        "items": items,
        "shipping_data": shipping_data,
        "shipping_details" : shipping_details
        }
        res = requests.post(self._ORDER_URL,json = data)
        id = res.json()['id']
        return id
 

    def payment_key_request(self, id : str, token : str) -> str:
        res = requests.post(self._PAYMENT_KEY_URL, json = {
        "auth_token": token,
        "amount_cents": self.total_price, 
        "expiration": 3600, 
        "order_id": id,
        "billing_data": self.billing_data, 
        "currency": "EGP",
        "integration_id": self._INTEGRATION_ID,
        "lock_order_when_paid": "false"
        })
        token = res.json()['token']
        return token


    def pay(self):
        if self.country.strip().lower() in ["egypt","egy"]:
            token = self.authentication_request()
            order_id = self.order_registration(token , items = self.items)
            payment_token = self.payment_key_request(id = order_id, token = token)
            return f"{self._PAY_URL}?payment_token={payment_token}"
        else:
            pass
