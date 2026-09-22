from concurrent.futures import ThreadPoolExecutor

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from automation.client import LabClient

pytestmark = pytest.mark.api

RESERVATION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["id", "sku", "quantity", "email", "status"],
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "sku": {"type": "string", "minLength": 1},
        "quantity": {"type": "integer", "minimum": 1, "maximum": 100},
        "email": {"type": "string", "format": "email"},
        "status": {"enum": ["active", "cancelled"]},
    },
}


def test_create_read_and_stock_contract(api):
    response = api.reserve(quantity=2)
    assert response.status_code == 201
    assert response.headers["Content-Type"].startswith("application/json")
    data = response.json()
    Draft202012Validator(RESERVATION_SCHEMA, format_checker=FormatChecker()).validate(data)
    assert data["sku"] == "TEA-001"
    assert data["quantity"] == 2
    assert data["email"] == "qa@example.com"
    assert data["status"] == "active"
    fetched = api.request("GET", f"/api/reservations/{data['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == data
    assert api.stock() == 8


@pytest.mark.parametrize("quantity", [0, -1, 101, 1.5, "2", True, None])
def test_invalid_quantity_does_not_change_stock(api, quantity):
    response = api.reserve(quantity=quantity)
    assert response.status_code == 422
    assert response.json() == {"error": "invalid_quantity"}
    assert api.stock() == 10


@pytest.mark.parametrize("quantity, status, expected_stock", [(1, 201, 9), (10, 201, 0), (11, 409, 10), (100, 409, 10)])
def test_quantity_boundaries_and_business_limit(api, quantity, status, expected_stock):
    response = api.reserve(quantity=quantity)
    assert response.status_code == status
    assert api.stock() == expected_stock
    if status == 409:
        assert response.json() == {"error": "insufficient_stock"}


@pytest.mark.parametrize("email", ["", "qa", "qa@", "qa @example.com", None])
def test_invalid_email(api, email):
    response = api.reserve(email=email)
    assert response.status_code == 422
    assert response.json() == {"error": "invalid_email"}
    assert api.stock() == 10


def test_unknown_product(api):
    response = api.reserve(sku="UNKNOWN")
    assert response.status_code == 404
    assert response.json() == {"error": "product_not_found"}
    assert api.stock() == 10


@pytest.mark.parametrize("method", ["GET", "DELETE"])
def test_unknown_reservation(api, method):
    response = api.request(method, "/api/reservations/unknown")
    assert response.status_code == 404
    assert response.json() == {"error": "reservation_not_found"}


@pytest.mark.parametrize("payload, content_type, expected", [("{", "application/json", 400), ("[]", "application/json", 422), ("x", "text/plain", 415)])
def test_bad_payload(api, payload, content_type, expected):
    response = api.request("POST", "/api/reservations", data=payload, headers={"Content-Type": content_type})
    assert response.status_code == expected
    assert api.stock() == 10


def test_key_required(api):
    response = api.request("POST", "/api/reservations", json={"sku": "TEA-001", "quantity": 1, "email": "qa@example.com"})
    assert response.status_code == 422
    assert response.json() == {"error": "invalid_idempotency_key"}
    assert api.stock() == 10


def test_replay_does_not_reserve_twice(api):
    first = api.reserve(quantity=3, key="retry-1")
    second = api.reserve(quantity=3, key="retry-1")
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    assert api.stock() == 7


def test_same_key_different_payload_is_conflict(api):
    assert api.reserve(quantity=3, key="retry-1").status_code == 201
    response = api.reserve(quantity=4, key="retry-1")
    assert response.status_code == 409
    assert response.json() == {"error": "idempotency_conflict"}
    assert api.stock() == 7


def test_cancel_is_idempotent(api):
    created = api.reserve(quantity=3)
    assert created.status_code == 201
    path = f"/api/reservations/{created.json()['id']}"
    for _ in range(2):
        response = api.request("DELETE", path)
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
        assert api.stock() == 10


def test_replay_after_cancel_does_not_reactivate(api):
    created = api.reserve(quantity=3, key="retry-1")
    assert api.request("DELETE", f"/api/reservations/{created.json()['id']}").status_code == 200
    replay = api.reserve(quantity=3, key="retry-1")
    assert replay.status_code == 200
    assert replay.json()["status"] == "cancelled"
    assert api.stock() == 10


def test_parallel_requests_cannot_oversell(api, lab):
    def reserve_once(_):
        client = LabClient(lab.url)
        try:
            return client.reserve(quantity=7).status_code
        finally:
            client.session.close()
    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(reserve_once, range(2)))
    assert sorted(statuses) == [201, 409]
    assert api.stock() == 3
