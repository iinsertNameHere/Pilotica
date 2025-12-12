import asyncio
import json
import os
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bcrypt import checkpw
from lib.blueprints.api import api_bp
from lib.blueprints.auth import auth_bp
from lib.blueprints.ui import ui_bp
from lib.models import Client, SessionLocal, User, init_db
from sanic import Request, Sanic, redirect, response
from sanic.exceptions import SanicException

init_db()

app = Sanic("Pilotica")
app.config["OAS_UI_DEFAULT"] = "swagger"
app.static("/static", "./static")

app.blueprint(ui_bp)
app.blueprint(auth_bp)
app.blueprint(api_bp)

os.environ["PILOTICA_START_TIME"] = datetime.now().strftime("%d-%m-%Y %H:%M")

@app.get("/")
async def index(request: Request):
    return redirect(app.url_for("ui.dashboard"))