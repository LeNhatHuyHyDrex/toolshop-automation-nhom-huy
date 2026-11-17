"""API tests for shopping cart: cart creation, adding items, and retrieving cart state.

Run:  pytest tests/api/test_carts_api.py -v
"""
import pytest

pytestmark = pytest.mark.api


@pytest.fixture
def new_cart(api):
    """Create a fresh cart for testing."""
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]


def test_cart_add_product_quantity_two_is_stored(api, new_cart):
    """Goal: cart API correctly stores added product quantity.
    Precondition: an empty cart and an existing product from catalog.
    Expected: GET /carts/{id} returns exactly 1 item with quantity 2 matching product_id."""
    products_response = api.get("/products")
    assert products_response.status == 200, products_response.text()
    product_id = products_response.json()["data"][0]["id"]

    add_response = api.post(f"/carts/{new_cart}", data={"product_id": product_id, "quantity": 2})
    assert add_response.status == 200, add_response.text()

    cart_response = api.get(f"/carts/{new_cart}")
    assert cart_response.status == 200, cart_response.text()
    items = cart_response.json()["cart_items"]
    assert len(items) == 1, items
    assert items[0]["quantity"] == 2
    assert items[0]["product_id"] == product_id
