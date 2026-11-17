"""Route interception and network mocking tests for Toolshop.

Run:  pytest tests/ui/test_network.py -v
"""
import json
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage

pytestmark = pytest.mark.ui

PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
EMPTY_PAGE = {
    "current_page": 1,
    "data": [],
    "from": None,
    "last_page": 1,
    "per_page": 9,
    "to": None,
    "total": 0,
}


def test_home_without_images_still_lists_products(page):
    """Goal: page remains functional and lists products even when image resources are blocked.
    Precondition: none.
    Expected: product names visible and at least one image request was blocked."""
    blocked = []

    def block_images(route):
        blocked.append(route.request.url)
        route.abort()

    page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block_images)
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    assert blocked, "no image request was blocked"


def test_home_with_empty_product_list_shows_no_results(page):
    """Goal: verify UI empty state when the API returns an empty product list.
    Precondition: route /products intercepted and fulfilled with empty data.
    Expected: message 'There are no products found.' is shown and 0 products displayed."""
    page.route(
        PRODUCT_LIST,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(EMPTY_PAGE),
        ),
    )
    home = HomePage(page).open()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


def test_home_when_product_api_fails_page_stays_usable(page):
    """Goal: verify resilience and graceful degradation when the product API returns 500.
    Precondition: route /products intercepted and fulfilled with HTTP 500 error.
    Expected: zero product cards displayed and the search box remains editable."""
    page.route(
        PRODUCT_LIST,
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({"message": "Internal Server Error"}),
        ),
    )
    home = HomePage(page).open()
    expect(home.product_names).to_have_count(0)
    expect(home.search_box).to_be_editable()
