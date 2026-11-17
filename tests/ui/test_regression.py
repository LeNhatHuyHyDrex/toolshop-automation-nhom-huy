"""Sprint 2 - regression UI tests covering all 6 functional groups:
1. Catalog & Search (sorting, empty search)
2. Filters (category checkbox, price slider)
3. Product Details (name, price verification)
4. Cart (line price calculation, continue shopping navigation)
5. Authentication (client-side required errors on empty login)
6. Contact & Account (logged-in user profile, file attachment upload, footer link in new tab)

Run:  pytest -m regression -v
"""
import pytest
from playwright.sync_api import expect

from pages.account_page import AccountPage
from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


# ---------------------------------------------------------------- Group 1: Catalog & Search
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
def test_search_unknown_keyword_shows_no_results_message(page):
    """Goal: empty search state displays friendly no-results message.
    Precondition: none.
    Expected: message 'There are no products found.' is shown and 0 products displayed."""
    home = HomePage(page).open().search("zzz-no-such-tool")
    expect(home.search_completed).to_be_visible()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


# ---------------------------------------------------------------- Group 2: Filters
@pytest.mark.regression
@pytest.mark.ui
def test_filter_by_category_shows_matching_products(page):
    """Goal: category filter shows only products belonging to the selected category.
    Precondition: none.
    Expected: all displayed products contain 'hammer' in their name."""
    home = HomePage(page).open().filter_by_category("Hammer")
    expect(home.product_names.first).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names, "no products found for category Hammer"
    assert all("hammer" in n.lower() for n in names), names


@pytest.mark.regression
@pytest.mark.ui
def test_filter_by_price_slider_adjusts_range(page):
    """Goal: price slider adjusts the maximum price filter.
    Precondition: none.
    Expected: slider aria-valuenow is reduced after pressing ArrowLeft."""
    home = HomePage(page).open()
    expect(home.slider_max).to_be_visible()
    initial_val = int(home.slider_max.get_attribute("aria-valuenow"))
    home.slider_max.focus()
    home.slider_max.press("ArrowLeft")
    home.slider_max.press("ArrowLeft")
    new_val = int(home.slider_max.get_attribute("aria-valuenow"))
    assert new_val < initial_val


# ---------------------------------------------------------------- Group 3: Product Details
@pytest.mark.regression
@pytest.mark.ui
def test_product_detail_shows_correct_name_and_price(page):
    """Goal: product detail page displays correct title and unit price.
    Precondition: product 'Claw Hammer' exists.
    Expected: product detail page displays 'Claw Hammer' and positive unit price."""
    home = HomePage(page).open()
    product = home.open_product("Claw Hammer")
    expect(product.name).to_have_text("Claw Hammer")
    assert product.price() > 0


# ---------------------------------------------------------------- Group 4: Cart
@pytest.mark.regression
@pytest.mark.ui
def test_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: shopping cart line total equals unit price multiplied by quantity.
    Precondition: empty cart.
    Expected: line price equals unit price times 2 and total matches line price sum."""
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_contain_text("Claw Hammer")
    unit_price = product.price()
    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")
    cart = product.go_to_cart()
    expect(cart.line_prices.first).to_be_visible()
    line_prices = cart.line_totals()
    assert line_prices[0] == pytest.approx(unit_price * 2)
    assert cart.total_value() == pytest.approx(sum(line_prices))


@pytest.mark.regression
@pytest.mark.ui
def test_regression_cart_continue_shopping_returns_to_home(page):
    """Goal: 'Continue Shopping' leads back to the product grid.
    Precondition: one product is in the cart.
    Expected: the product grid is visible again."""
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_contain_text("Claw Hammer")
    product.add_to_cart()
    expect(product.cart_quantity).to_have_text("1")
    cart = product.go_to_cart()
    expect(cart.product_titles).to_have_count(1)
    cart.continue_shopping.click()
    expect(HomePage(page).product_names.first).to_be_visible()


# ---------------------------------------------------------------- Group 5: Authentication
@pytest.mark.regression
@pytest.mark.ui
def test_login_empty_form_shows_required_errors(page):
    """Goal: client-side validation displays error messages when submitting empty login.
    Precondition: none.
    Expected: 'Email is required' and 'Password is required' error messages appear."""
    login = LoginPage(page).open()
    login.submit_button.click()
    expect(login.email_error).to_contain_text("Email is required")
    expect(login.password_error).to_contain_text("Password is required")


# ---------------------------------------------------------------- Group 6: Contact & Account
@pytest.mark.regression
@pytest.mark.ui
def test_account_page_logged_in_shows_user_profile(logged_in_page):
    """Goal: reuse saved authentication state to access account page directly.
    Precondition: logged in once via auth_state session fixture.
    Expected: account title displays 'My account' and user navigation shows 'QA Bot'."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")


@pytest.mark.regression
@pytest.mark.ui
def test_contact_attachment_empty_file_submits_successfully(page, tmp_path):
    """Goal: contact form accepts zero-byte file attachment and submits successfully.
    Precondition: a 0-byte temporary file exists.
    Expected: contact form submission succeeds with confirmation message."""
    empty_file = tmp_path / "empty_doc.txt"
    empty_file.write_text("", encoding="utf-8")
    contact = (
        ContactPage(page)
        .open()
        .fill_form(
            "QA",
            "Tester",
            "tester@example.com",
            "Customer service",
            "Hello, I am testing the file attachment feature with a detailed message.",
        )
        .attach(str(empty_file))
        .submit()
    )
    expect(contact.success).to_contain_text("Thanks for your message! We will contact you shortly.")


@pytest.mark.regression
@pytest.mark.ui
def test_footer_github_link_opens_in_new_tab(page):
    """Goal: GitHub footer link opens target repository in a new tab.
    Precondition: home page is loaded.
    Expected: a new browser tab opens with the GitHub URL."""
    home = HomePage(page).open()
    with page.context.expect_page() as new_tab_info:
        home.footer_github_link.click()
    new_page = new_tab_info.value
    new_page.wait_for_load_state()
    assert "github.com" in new_page.url
