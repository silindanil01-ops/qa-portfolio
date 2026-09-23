"""HTTP client: explicit timeouts, no implicit retries of state-changing calls."""
import uuid
import requests


class LabClient:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.trust_env = False  # The lab is loopback-only; ignore proxy settings.

    def request(self, method, path, **kwargs):
        return self.session.request(method, f"{self.url}{path}", timeout=5, **kwargs)

    def reserve(self, *, sku="TEA-001", quantity=1, email="qa@example.com", key=None):
        return self.request("POST", "/api/reservations", json={"sku": sku, "quantity": quantity, "email": email}, headers={"Idempotency-Key": key or str(uuid.uuid4())})

    def stock(self, sku="TEA-001"):
        response = self.request("GET", "/api/products")
        response.raise_for_status()
        return next(product["stock"] for product in response.json() if product["sku"] == sku)
