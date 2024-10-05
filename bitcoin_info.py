import config
import requests

from db.database import CacheManager

from requests.exceptions import RequestException
from flask.views import MethodView
from flask_limiter import Limiter
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError, HTTPException
from functools import wraps


class TooManyRequests(HTTPException):
    """*429* `Too Many Request`

    The server is limiting the rate at which the client can send requests.
    """

    code = 429
    description = (
        "The server is limiting the rate at which the client can send requests."
    )


def handle_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = f(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 400:
                raise BadRequest("Bad request")
            elif status_code == 404:
                raise NotFound("Resource not found")
            else:
                raise InternalServerError("Internal server error")

        return data

    return decorated_function


def rate_limit(limit_string):
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            limiter = getattr(self, "_limiter", None)
            if limiter:
                limited = limiter.limit(limit_string)(f)
                return limited(self, *args, **kwargs)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


class Service(MethodView):
    def __init__(self, config: config.Config, limiter: Limiter):
        self._endpoint = config["api"]["endpoint"]
        self._timeout = config["api"]["timeout"]
        self._limiter = limiter

    @handle_response
    def retrieve(self, url):
        response = requests.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.json()


class AddressService(Service):
    """
    AddressInfoService class, which is responsible for communication with the
    https://blockchain.info API, to retrieve information about Bitcoin addresses.
    """

    def __init__(self, config: config.Config, cache: CacheManager, limiter: Limiter):
        super().__init__(config, limiter)
        self._cache = cache

    @rate_limit("10 per minute")
    def get(self, address: str) -> dict:
        """
        Get address details for the given address.

        Parameters:
        - address (str): The Bitcoin address.

        Returns:
        - dict: A dictionary containing the address details
          {
            "address": str,
            "balance": int,
            "transaction_count": int,
          }
        """
        if not address:
            raise BadRequest("Missing address parameter")

        address_result = self._cache.get(address, "address")
        if address_result:
            return address_result

        url = f"{self._endpoint}/rawaddr/{address}"
        print(f"Sending request to {url}")
        data = self.retrieve(url)

        if len(data) == 0:
            raise NotFound(f"Transaction not found: {address}")

        transaction_count = data["n_tx"]
        balance = data["final_balance"]
        address_result = {
            "address": address,
            "balance": data["final_balance"],
            "transaction_count": data["n_tx"],
        }
        self._cache.put(address, address_result, "address")
        return address_result


class TransactionService(Service):
    """
    TransactionService class, which is responsible for communication with the
    https://blockchain.info API, to retrieve information about Bitcoin transactions.
    """

    def __init__(self, config: config.Config, cache: CacheManager, limiter: Limiter):
        super().__init__(config, limiter)
        self._cache = cache

    @rate_limit("5 per minute")
    def get(self, txhash: str) -> dict:
        """
        Get transaction details for the given transaction hash.

        Parameters:
        - txhash (str): The transaction hash.

        Returns:
        - dict: A dictionary containing the transaction details
          {
            "hash": str,
            "fee": int,
            "transaction_index": int,
            "block_time": int,
            "inputs": [
                {
                    "address": str,
                    "value": int,
                },
                ...
            ],
            "outputs": [
                {
                    "address": str,
                    "value": int,
                },
                ...
          }
        """
        if not txhash:
            raise BadRequest("Missing txhash parameter")

        tx_result = self._cache.get(txhash, "transaction")
        if tx_result:
            print(f"Transaction found in cache: {txhash}")
            return tx_result

        url = f"{self._endpoint}/rawtx/{txhash}"
        print(f"Sending request to {url}")
        data = self.retrieve(url)

        if len(data) == 0:
            raise NotFound(f"Transaction not found: {txhash}")

        tx_result = {
            "hash": data["hash"],
            "fee": data["fee"],
            "transaction_index": data["tx_index"],
            "block_time": data["time"],
            "inputs": [
                {
                    "address": item.get("prev_out", {}).get("addr", "Unknown"),
                    "value": item.get("prev_out", {}).get("value", 0),
                }
                for item in data.get("inputs", [])
            ],
            "outputs": [
                {
                    "address": item.get("addr", "Unknown"),
                    "value": item.get("value", 0),
                }
                for item in data.get("out", [])
            ],
        }

        self._cache.put(txhash, tx_result, "transaction")
        return tx_result
