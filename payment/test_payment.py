import os
import pytest
from unittest.mock import patch, AsyncMock

os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"
os.environ["REDIS_PASSWORD"] = ""

from fastapi.testclient import TestClient
from main import app, Order
from redis_om import NotFoundError

client = TestClient(app)

# --- UNIT ---
def test_unit_logic():
    order = Order(product_id="p1", price=100.0, fee=20.0, total=120.0, quantity=1, status="pending")
    assert order.fee == 20.0
    assert order.status == "pending"

# --- INTEGRACIONI ---
def test_integration_db():
    order = Order(product_id="int_p1", price=100.0, fee=20.0, total=120.0, quantity=1, status="pending")
    order.save()
    assert Order.get(order.pk).product_id == "int_p1"

# --- FUNKCIONALNI ---
@patch('main.Order.get')
def test_api_404(mock_get):
    mock_get.side_effect = NotFoundError()
    resp = client.get("/orders/999")
    assert resp.status_code == 404

@patch('main.httpx.AsyncClient.get', new_callable=AsyncMock)
@patch('main.process_order')
def test_api_post(mock_proc, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": "p1", "price": 100.0}
    resp = client.post("/orders", json={"id": "p1", "quantity": 1})
    assert resp.status_code == 200