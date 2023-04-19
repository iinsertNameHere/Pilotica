# Normal imports
import os
import secrets
import yaml

# Flask imports
from pilotica.custom_flask import CustomFlask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask import request, redirect, url_for
from pilotica.transport import Transport

# Blueprint imports
from .service import service, init_service, __main__ as __service_main__
from .webinterface import webinterface
from .auth import auth

# pilotica imports
from .database import db, Pilot
from .config import Config
from .console import Color
from .components.engine import ComponentManager, Component

import pilotica.settings as ps
import pilotica.pilots as pilots

component_manager = ComponentManager()

def setup_app(name, db_name="session.db"):
    # create the app
    app = CustomFlask(name)

    # setting up yaml config
    config_path = os.path.join(app.instance_path, "config", "config.yaml")
    config = Config(app.instance_path, config_path)

    if os.path.isfile(config_path):
        config.load()
    else:
        config.create()

    # configuring the app
    if config.pilotica["secret_key"] == "RANDOM":
        secret_key = secrets.token_urlsafe(16)
    else:
        secret_key = config.pilotica["secret_key"]

    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    db.init_app(app)
    ps.login_manager.init_app(app)

    @ps.login_manager.user_loader
    def load_user(id):
        return Pilot.query.get(int(id))

    ps.secret_key = secret_key

    with app.app_context():
        db.create_all()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.mkdir(os.path.join(app.instance_path, "config"))
        os.mkdir(os.path.join(app.instance_path, "components"))
    except OSError:
        pass

    # create pilots
    with app.app_context():
        if not len(Pilot.query.all()) > 0:
            initial_pilot = Pilot(name="adminpilot", pwd_hash=generate_password_hash("admin"), role='ADMIN')
            db.session.add(initial_pilot)
            db.session.commit()


    # add blueprints
    app.register_blueprint(service)
    app.register_blueprint(webinterface)
    app.register_blueprint(auth)

    #Init Components
    for component in config.component_list:
        component_manager.add(Component(app.instance_path, component.get("alias"), logging=component.get("logging")))

    if len(component_manager.components.get("all")) > 0:
        print()

    # Init Globals
    ps.component_manager = component_manager

    service_conf = {
        "online": True,
        "logging": config.pilotica.get("API_LOGGING"),
        "secret_key": secret_key
    }
    init_service(service_conf, service_dict=__service_main__.__dict__)

    @app.route("/transport/load", methods = {'GET'})
    def transport_load():
        data = request.args.get("data")
        return Transport(data).load()

    @app.route("/transport/dump", methods = {'GET'})
    def transport_dump():
        data = request.args.get("data")
        return Transport(data).dump()

    @app.route("/")
    def index():
        return redirect(url_for('webinterface.agents'))

    return app, config