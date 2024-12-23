from sanic import Blueprint, Request
from sanic.response import json, redirect
from sanic.exceptions import Unauthorized
from sanic_ext import render
from ..error import error_redirect
from ..models import User, SessionLocal
from ..authentication import create_access_token

auth_bp = Blueprint("auth", url_prefix="/auth")

@auth_bp.get("/login")
async def login(request: Request):
    return await render("login.html.j2")

@auth_bp.post("/login")
async def login_action(request: Request):
    # Get form data
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return error_redirect(request, "Invalid Username or Password")

    # Fetch the user from the database
    with SessionLocal() as session:
        user = session.query(User).filter(User.name == username).first()

    if not user or not user.check_password(password):
        return error_redirect(request, "Invalid Username or Password")

    # Create access token
    access_token = create_access_token(data={"sub": str(user.uuid)})

    # Set the token in cookies
    response = redirect("/")
    response.cookies["access_token"] = access_token
    return response

@auth_bp.get("/logout")
async def logout(request: Request):
    """
    Clears the user's access token and redirects them to the login page.
    """
    response = redirect("/auth/login")  # Redirect to login page after logout
    # Expire the cookie to remove the access token
    response.cookies["access_token"] = ""
    response.cookies["access_token"]["max-age"] = 0  # Set max-age to 0 to expire the cookie immediately
    return response