"""Sprint 1 (extra) - regression tests on sorting and cart navigation, written with page objects.

Run:  pytest -m regression

Rules (same as the final project):
- No locator in this file: locators live in pages/.
- No assertion in pages/: assertions live here.
- No fixed waits: wait with expect().
- Every test has a 3-line docstring: goal, precondition, expected.
"""
import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage


@pytest.mark.regression
@pytest.mark.ui
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_regression_sort_by_price_orders_products(page, order):
    """Goal: sorting by price orders the product grid.
    Precondition: none.
    Expected: prices on the first page are sorted in the chosen direction."""
    home = HomePage(page).open().sort_by(order)
    expect(home.sorting_completed).to_be_visible()
    prices = home.prices()
    assert prices, "no prices on the first page"
    assert prices == sorted(prices, reverse=order.endswith("desc"))


@pytest.mark.regression
@pytest.mark.ui
def test_regression_cart_continue_shopping_returns_to_home(page):
    """Goal: 'Continue Shopping' leads back to the product grid.
    Precondition: one product is in the cart.
    Expected: the product grid is visible again."""
    cart = HomePage(page).open().open_product("Claw Hammer").add_to_cart().go_to_cart()
    expect(cart.product_titles).to_have_count(1)
    cart.continue_shopping.click()
    expect(HomePage(page).product_names.first).to_be_visible()
