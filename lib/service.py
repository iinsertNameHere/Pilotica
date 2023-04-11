from flask import Blueprint
from flask import request

# API Service
service = Blueprint("service", __name__, url_prefix="/service")

api_service_online = True

@service.route("/", methods = {"GET"})
def status():
    if api_service_online:
        return "online"
    else:
        return "offline"

@service.route("/bind", methods = {"POST"})
def bind():
    ip = request.remote_addr
    request.data
