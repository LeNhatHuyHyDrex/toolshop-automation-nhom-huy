"""API tests for users: validation, password policies, and authenticated endpoints.

Run:  pytest tests/api/test_users_api.py -v
"""
import pytest

from conftest import new_email, register_user, strong_password

pytestmark = pytest.mark.api


def test_register_empty_body_returns_422_with_field_errors(api):
    """Goal: server-side validation on empty registration.
    Precondition: none.
    Expected: 422 and error lists for 'email' and 'password'."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    body = response.json()
    assert isinstance(body.get("email"), list) and body["email"], body
    assert isinstance(body.get("password"), list) and body["password"], body


def test_register_leaked_password_is_rejected(api):
    """Goal: password policy rejects commonly leaked passwords.
    Precondition: none.
    Expected: 422 because 'Welcome01!' appears in known data leaks."""
    response = register_user(api, new_email(), "Welcome01!")
    assert response.status == 422, response.text()
    body = response.json()
    assert isinstance(body.get("password"), list) and body["password"], body


def test_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: bearer token grants access to protected profile.
    Precondition: user registered and logged in by fixtures.
    Expected: 200 and profile contains matching registered email."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]


def test_register_response_does_not_expose_password(api):
    """Goal: registration endpoint does not expose secrets.
    Precondition: none.
    Expected: 201 and no 'password' key in the JSON body."""
    response = register_user(api, new_email(), strong_password())
    assert response.status == 201, response.text()
    assert "password" not in response.json(), response.json()
