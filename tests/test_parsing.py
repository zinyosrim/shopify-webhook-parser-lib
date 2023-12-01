# python -m unittest discover tests
import unittest
from azure.functions import HttpRequest
from shopifywebhookparser.parsing import create_parsed_webhook, azure_strategy
from unittest.mock import patch
from shopifywebhookparser.models import ParsedWebhook


class TestParsingFunctions(unittest.TestCase):
    def setUp(self):
        self.headers = {
            "X-Shopify-Shop-Domain": "example.myshopify.com",
            "X-Shopify-Hmac-Sha256": "test_hmac",
            "X-Shopify-Topic": "orders/create",
        }
        self.lowercase_headers = {k.lower(): v for k, v in self.headers.items()}
        self.body = '{"test": "data"}'
        self.req = HttpRequest(
            method="POST",
            url="http://example.com",
            headers=self.lowercase_headers,
            body=self.body.encode(),  # Ensure body is bytes
        )

    def test_azure_strategy(self):
        body, headers = azure_strategy(self.req)
        self.assertIsInstance(body, bytes)  # Ensure body is bytes
        self.assertEqual(body.decode(), self.body)  # Compare as strings
        self.assertEqual(
            dict(headers), self.lowercase_headers
        )  # Convert headers to dict and compare

    @patch("shopifywebhookparser.parsing.json.loads")
    def test_create_parsed_webhook(self, mock_json_loads):
        mock_json_loads.return_value = {"test": "data"}
        webhook = create_parsed_webhook(self.req, azure_strategy)
        self.assertEqual(webhook.payload, {"test": "data"})
        self.assertEqual(dict(webhook.attributes), self.lowercase_headers)
        self.assertEqual(webhook.source_url, self.headers["X-Shopify-Shop-Domain"])
        self.assertEqual(webhook.onlinestore_name, "example")
        self.assertEqual(webhook.topic, self.headers["X-Shopify-Topic"])


if __name__ == "__main__":
    unittest.main()
