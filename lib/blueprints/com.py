from sanic import Blueprint, Request, raw, empty
from ..models import User, SessionLocal, Client
from ..authentication import authenticated, get_authenticated_user

com_bp = Blueprint("com", url_prefix="/com")