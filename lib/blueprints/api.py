from sanic import Blueprint, Request, raw, empty
from ..models import User, SessionLocal, Client
from ..authentication import authenticated, get_authenticated_user
from ..premissions import Premissions
from datetime import datetime, timedelta

api_bp = Blueprint("api", url_prefix="/api")

@api_bp.get("/users/<id>/image.png")
async def userpng(request: Request, id: int):
    error = authenticated(request, allow_api_key=True, return_json=True)
    if error: return empty(status=404)

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == id).first()

    if not user:
        return empty(status=404)

    return raw(user.image, content_type="image/png")

@api_bp.get("/client/<id>/logins.txt")
async def client_logins_txt(request: Request, id: int):
    error = authenticated(request, allow_api_key=True, return_json=True)
    if error: return empty(status=404)

    with SessionLocal() as session:
        client = session.query(Client).filter(Client.id == id).first()

    if not client:
        return empty(status=404)

    return raw(
        client.logins_file,
        content_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="client{id}_logins.txt"'
        }
    )

@api_bp.get("/client/<id>/cookies.txt")
async def client_cookies_txt(request: Request, id: int):
    error = authenticated(request, allow_api_key=True, return_json=True)
    if error: return empty(status=404)

    with SessionLocal() as session:
        client = session.query(Client).filter(Client.id == id).first()

    if not client:
        return empty(status=404)

    return raw(
        client.cookies_file,
        content_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="client{id}_cookies.txt"'
        }
    )