from sanic import Blueprint, Request
from sanic_ext import render
from ..authentication import authenticated, get_authenticated_user
from ..premissions import Premissions
from datetime import datetime
import os

ui_bp = Blueprint("ui")

geolocation_example_data = """[
    ['Washington, US', '38.9014', '-77.0504', 8, ['154.41.74.1']],
    ['Clifton Forge, US', '37.8162', '-79.8245', 1, ['64.4.96.1']],
    ['Mexico City, MX', '19.4285', '-99.1277', 1, ['38.104.249.201']],
    ['Al Aḩmadī, KW', '29.0769', '48.0839', 1, ['193.188.48.1']],
    ['Drammen, NO', '59.7458', '10.2305', 20, ['84.19.147.41']],
    ['Las Vegas, US', '36.1750', '-115.1372', 1, ['205.185.119.31']],
    ['Dumfries, GB', '55.0696', '-3.6114', 1, ['195.95.134.1']],
    ['Madrid, ES', '40.4165', '-3.7026', 2, ['192.148.204.1']],
    ['Bengaluru, IN', '12.9719', '77.5937', 1, ['103.208.248.1']],
    ['San Carlos, US', '37.5072', '-122.2605', 1, ['192.153.122.1']],
    ['Mumbai, IN', '19.0728', '72.8826', 1, ['169.136.109.1']],
    ['Des Moines, US', '41.6005', '-93.6091', 1, ['63.230.61.221']],
    ['Amsterdam, NL', '52.3740', '4.8897', 1, ['194.110.22.1']],
    ['Winterthur, CH', '47.4931', '8.7297', 1, ['193.5.126.1']],
    ['Bell, US', '33.9775', '-118.1870', 1, ['109.72.121.1']],
    ['Perm, RU', '58.0105', '56.2502', 1, ['46.146.112.11']],
    ['Chisinau, MD', '47.0056', '28.8575', 1, ['94.158.246.1']],
    ['Ang Mo Kio New Town, SG', '1.3803', '103.8397', 1, ['202.12.94.1']],
    ['Al Fujairah City, AE', '25.1164', '56.3414', 1, ['23.206.197.1']],
    ['Chicago, US', '41.8500', '-87.6500', 2, ['149.52.0.1', '64.181.192.1']],
    ['Marne La Vallée, FR', '48.8358', '2.6424', 1, ['185.69.76.1']],
    ['London, GB', '51.5085', '-0.1257', 1, ['198.244.135.41']],
    ['Bab Ezzouar, DZ', '36.7261', '3.1829', 1, ['104.28.161.191']],
    ['Ljubljana, SI', '46.0511', '14.5051', 1, ['82.214.74.121']],
    ['Tokyo, JP', '35.6895', '139.6917', 1, ['203.192.128.1']],
    ['Matsumoto, JP', '36.3089', '138.0559', 1, ['202.135.150.111']],
    ['Shanghai, CN', '31.2222', '121.4581', 1, ['58.192.0.1']]
]"""

def get_uptime():
    start_time_str = os.environ.get("PILOTICA_START_TIME")
    if not start_time_str: return "0s"

    start_time = datetime.strptime(start_time_str, "%d-%m-%Y %H:%M")

    difference = datetime.now() - start_time
    seconds = difference.total_seconds()
    minutes = int(seconds / 60)
    hours = int(seconds / (60 * 60))
    days = int(seconds / (60 * 60 * 24))

    return (f"{days}d" if days > 0 else "") + (f"{hours}h" if hours > 0 else "") + (f"{minutes}m" if minutes > 0 else f"{int(seconds)}s") 

@ui_bp.get("/dashboard")
async def dashboard(request: Request):
    error = authenticated(request)
    if error: return error
    user = get_authenticated_user(request)
    return await render("dashboard.html.j2", context={
        "active": "dashboard", "user": user.to_json(), "premissions": Premissions.to_json(),
        "ipLocations": geolocation_example_data, "uptime": get_uptime(), "newClientClounts": "[1, 0, 3]",
        "users": [{"id": 1, "name": "admin"}, {"id": 1, "name": "fluffyman1"}, {"id": 1, "name": "simbamba"}, {"id": 1, "name": "rucky1510"}]})

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