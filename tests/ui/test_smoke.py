"""Sprint 1 - 4 smoke tests on Toolshop, written with page objects.

Run:  pytest -m smoke

Rules (same as the final project):
- No locator in this file: locators live in pages/.
- No assertion in pages/: assertions live here.
- No fixed waits: wait with expect().
- Every test has a 3-line docstring: goal, precondition, expected.
"""
import re

import pytest
from playwright.sync_api import expect

from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_search_keyword_shows_only_matching_products(page):
    """Goal: search filters the product grid.
    Precondition: none.
    Expected: caption shows the keyword and every product name contains it."""
    home = HomePage(page).open().search("pliers")
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("pliers")
    names = home.product_names.all_inner_texts()
    assert names, "search returned no products"
    assert all("pliers" in n.lower() for n in names), names


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_add_claw_hammer_quantity_three_updates_cart_badge(page):
    """Goal: add-to-cart uses the chosen quantity.
    Precondition: product 'Claw Hammer' exists.
    Expected: the cart badge in the menu shows 3."""
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_contain_text("Claw Hammer")
    product.add_to_cart(quantity=3)
    expect(product.cart_quantity).to_have_text("3")


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_login_unknown_email_shows_error_and_stays_on_login(page):
    """Goal: invalid credentials are rejected.
    Precondition: an e-mail with no account (never a shared account: Toolshop locks it after 3 failures).
    Expected: 'Invalid email or password' and the URL still ends with /auth/login."""
    login = LoginPage(page).open().login("nobody-here@example.com", "Wrong-Password-123")
    expect(login.error).to_contain_text("Invalid email or password")
    expect(page).to_have_url(re.compile(r"/auth/login$"))


@pytest.mark.smoke
@pytest.mark.ui
def test_smoke_contact_empty_form_shows_required_errors(page):
    """Goal: client-side validation of the contact form.
    Precondition: none.
    Expected: 'Subject is required' and 'Message is required'."""
    contact = ContactPage(page).open().submit()
    expect(contact.errors.filter(has_text="Subject is required")).to_be_visible()
    expect(contact.errors.filter(has_text="Message is required")).to_be_visible()
