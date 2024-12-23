from sanic import Blueprint, Request
from sanic_ext import render
from ..authentication import authenticated, get_authenticated_user
from ..premissions import Premissions

ui_bp = Blueprint("ui")

@ui_bp.get("/dashboard")
async def dashboard(request: Request):
    error = authenticated(request)
    if error: return error
    user = get_authenticated_user(request)
    return await render("dashboard.html.j2", context={"active": "dashboard", "user": user.to_json(), "premissions": Premissions.to_json()})

@ui_bp.get("/clients")
async def clients(request: Request):
    error = authenticated(request)
    if error: return error
    user = get_authenticated_user(request)
    return await render("clients.html.j2", context={"active": "clients", "user": user.to_json(), "premissions": Premissions.to_json()})

@ui_bp.get("/settings")
async def settings(request: Request):
    error = authenticated(request, permissions=[Premissions.Configurator], redirect_route="/dashboard")
    if error: return error
    user = get_authenticated_user(request)
    return await render("settings.html.j2", context={"active": "settings", "user": user.to_json(), "premissions": Premissions.to_json()})