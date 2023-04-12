import os
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .service import service, serviceConf
from .database import db
from .config import Config
from .plugins.pluginUtils import PluginManager, Plugin

plugin_manager = PluginManager()

def setup_app(name, db_name="pilot.db", secret_key=secrets.token_urlsafe(16)):
    # create and configure the app
    app = Flask(name)
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # add blueprints
    serviceConf["secret_key"] = secret_key
    app.register_blueprint(service)

    # setting up yaml config
    config_path = os.path.join(app.instance_path, "config", "config.yaml")
    config = Config(app.instance_path, config_path)

    if os.path.isfile(config_path):
        config.load()
    else:
        config.create()

    serviceConf["logging"] = config.pilot.get("API_LOGGING")

    #Init Plugins
    for plugin in config.plugin_list:
        plugin_manager.add(Plugin(app.instance_path, plugin))

    return app, config