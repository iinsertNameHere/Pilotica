import os
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .service import service, serviceConf
from .database import db


def setup_app(name, db_name="pilot.db", api_logging = False, secret_key=secrets.token_urlsafe(16)):
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
    serviceConf["logging"] = api_logging
    serviceConf["secret_key"] = secret_key
    app.register_blueprint(service)

    return app