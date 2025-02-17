from sanic import Blueprint, Request, empty

service_bp = Blueprint("service", url_prefix="/service")

@service_bp.get("/")
async def status(request: Request, id: id):
    return empty(status=200)