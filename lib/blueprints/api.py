from sanic import Blueprint, Request, raw, empty
from ..models import User, SessionLocal
from ..authentication import authenticated, get_authenticated_user
from ..premissions import Premissions

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
