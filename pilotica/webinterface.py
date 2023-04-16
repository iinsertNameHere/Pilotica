from flask import Blueprint
from flask import request
import json

from .console import Color
from .database import *
from .transport import Transport
from .settings import secret_key
from .pilots import PilotRoles

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# Webinterface
webinterface = Blueprint("webinterface", __name__, url_prefix="/interface")

@webinterface.route("")
@webinterface.route("/")
def interface():
    return redirect(url_for('webinterface.agents'))

@webinterface.route("/agents")
@login_required
def agents():
    agents: list[Agent] = Agent.query.all()
    return render_template("agents.html.j2",
            agents=[agent.jsonify(asDict=True) for agent in agents],
            Transport=Transport, 
            current_pilot=current_user)

@webinterface.route("/pilots")
@login_required
def pilots():
    if current_user.role == PilotRoles.ADMIN.get('name'):
        pilots: list[Pilot] = Pilot.query.all()
        return render_template('pilots.html.j2' ,
                pilots=[pilot.jsonify(asDict=True) for pilot in pilots],
                Transport=Transport, 
                current_pilot=current_user)
    else:
        flash("You don't have have the right permissions!", 'danger')
        return redirect(request.referrer)