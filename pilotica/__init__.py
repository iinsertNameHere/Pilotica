# Normal imports
import os
import secrets

# Flask imports
from pilotica.custom_flask import CustomFlask
from flask_sqlalchemy import SQLAlchemy

# Blueprint imports
from .service import service, init_service, __main__ as __service_main__
from .webinterface import webinterface

# pilotica imports
from .database import db
from .config import Config
from .plugin.engine import PluginManager, Plugin

import pilotica.settings as ps

plugin_manager = PluginManager()

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

    with app.app_context():
        db.create_all()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, "config"))
        os.makedirs(os.path.join(app.instance_path, "plugins"))
    except OSError:
        pass

    # add blueprints
    app.register_blueprint(service)
    app.register_blueprint(webinterface)

    #Init Plugins
    for plugin in config.plugin_list:
        plugin_manager.add(Plugin(app.instance_path, plugin["alias"], logging=plugin["logging"]))

    if len(plugin_manager.plugins["all"]) > 0:
        print()

    ps.plugin_manager = plugin_manager

    service_conf = {
        "online": True,
        "logging": config.pilotica.get("API_LOGGING"),
        "secret_key": secret_key
    }
    init_service(service_conf, service_dict=__service_main__.__dict__)

    return app, config