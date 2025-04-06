import hashlib
import hmac

import requests
import time

from urllib.parse import urlencode


class BinanceTestClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://testnet.binance.vision/api'

    def _generate_signature(self, query_string: str) -> str:
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _execute_request(self, endpoint: str, params: dict, method: str = 'GET'):
        timestamp = int(time.time() * 1000)
        params['timestamp'] = timestamp

        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature

        headers = {
            'X-MBX-APIKEY': self.api_key
        }

        if method == 'GET':
            return requests.get(f"{self.base_url}{endpoint}", params=params, headers=headers)

        return requests.post(f"{self.base_url}{endpoint}", params=params, headers=headers)


    def get_account_info(self):
        endpoint = "/v3/account"
        params = {}
        response = self._execute_request(endpoint, params)
        return response.json()

    def get_price(self, symbol: str):
        endpoint = "/v3/ticker/price"
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params={"symbol": symbol.upper()})
        return response.json()

    def get_candlesticks(self, symbol: str, interval: str = '1h', limit: int = 50):
        endpoint = "/v3/klines"
        url = f"{self.base_url}{endpoint}"
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        response = requests.get(url, params=params)
        return response.json()

    def create_order(self, order: dict):
        endpoint = "/v3/order/test" if order.get("test") else "/v3/order"
        params = {
            "symbol": order["symbol"],
            "side": order["side"],
            "type": order["order_type"],
            "quantity": order["quantity"],
        }
        return self._execute_request(endpoint, params, method='POST').json()
