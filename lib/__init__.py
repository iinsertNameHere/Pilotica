import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .service import service


def setup_app(dbName="pilot.db"):
    # create and configure the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "key"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{dbName}'
    db = SQLAlchemy(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # add blueprints
    app.register_blueprint(service)

    return app, db