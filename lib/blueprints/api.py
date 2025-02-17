from sanic import Blueprint, Request, raw, empty
from ..models import User, SessionLocal, Client
from ..authentication import authenticated, get_authenticated_user
from ..premissions import Premissions
from ..misc import create_ip_groups, get_ip_groups
from datetime import datetime, timedelta

api_bp = Blueprint("api", url_prefix="/api")

@api_bp.get("/users/<id>/image.png")
async def userpng(request: Request, id: id):
    error = authenticated(request, allow_api_key=True, return_json=True)
    if error: return empty(status=404)

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == id).first()

    if not user:
        return empty(status=404)

    return raw(user.image, content_type="image/png")

@api_bp.get("/cig")
async def cig(request: Request):
    error = authenticated(request, allow_api_key=True, return_json=True)
    if error: return empty(status=405)

    time, _ = get_ip_groups()
    if time:
        if time + timedelta(minutes=10) > datetime.now():
            return empty(status=200)

    print("Fetching Geolocations!")

    with SessionLocal() as session:
        clients = session.query(Client).all()
    await create_ip_groups([c.ip for c in clients])

    return empty(status=200)