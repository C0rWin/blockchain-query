import unittest
from unittest.mock import Mock, patch
import requests
from flask_limiter import Limiter
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from bitcoin_info import AddressService, TransactionService, TooManyRequests


class TestBitcoinInfo(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            "api": {"endpoint": "https://blockchain.info", "timeout": 10}
        }
        self.mock_cache = Mock()
        self.mock_limiter = Mock(spec=Limiter)
        self.address_service = AddressService(self.mock_config, self.mock_cache, None)
        self.transaction_service = TransactionService(
            self.mock_config, self.mock_cache, None
        )

    @patch("requests.get")
    def test_address_service_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"final_balance": 100000, "n_tx": 5}
        mock_get.return_value = mock_response
        self.mock_cache.get.return_value = None

        result = self.address_service.get("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

        self.assertEqual(result["address"], "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        self.assertEqual(result["balance"], 100000)
        self.assertEqual(result["transaction_count"], 5)
        self.mock_cache.put.assert_called_once()

    def test_address_service_get_cached(self):
        self.mock_cache.get.return_value = {
            "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "balance": 100000,
            "transaction_count": 5,
        }

        result = self.address_service.get("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

        self.assertEqual(result["address"], "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        self.assertEqual(result["balance"], 100000)
        self.assertEqual(result["transaction_count"], 5)
        self.mock_cache.get.assert_called_once()
        self.mock_cache.put.assert_not_called()

    def test_address_service_get_missing_address(self):
        with self.assertRaises(BadRequest):
            self.address_service.get("")

    @patch("requests.get")
    def test_address_service_get_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        self.mock_cache.get.return_value = None

        with self.assertRaises(NotFound):
            self.address_service.get("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

    @patch("requests.get")
    def test_address_service_get_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException()
        self.mock_cache.get.return_value = None

        with self.assertRaises(InternalServerError):
            self.address_service.get("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

    @patch("requests.get")
    def test_transaction_service_get_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "hash": "abc123",
            "fee": 100,
            "tx_index": 1,
            "time": 1630000000,
            "inputs": [
                {"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "value": 50000}
            ],
            "out": [{"address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "value": 50000}],
        }

        mock_get.return_value = mock_response
        self.mock_cache.get.return_value = None

        result = self.transaction_service.get("abc123")

        self.assertEqual(result["hash"], "abc123")
        self.assertEqual(result["fee"], 100)
        self.assertEqual(result["transaction_index"], 1)
        self.assertEqual(result["block_time"], 1630000000)
        self.assertEqual(len(result["inputs"]), 1)
        self.assertEqual(len(result["outputs"]), 1)
        self.mock_cache.put.assert_called_once()


if __name__ == "__main__":
    unittest.main()
