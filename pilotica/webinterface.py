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

from werkzeug.security import generate_password_hash

# Webinterface
webinterface = Blueprint("webinterface", __name__, url_prefix="/interface")

@webinterface.route("")
@webinterface.route("/")
def interface():
    return redirect(url_for('webinterface.agents'))

@webinterface.route("/agents", methods = {'GET'})
@login_required
def agents():
    agents: list[Agent] = Agent.query.all()
    return render_template("agents.html.j2",
            agents=[agent.jsonify(asDict=True) for agent in agents],
            Transport=Transport, 
            current_pilot=current_user)

@webinterface.route("/pilots/new", methods = {'POST'})
@login_required
def new_pilot():
    print(request.form)
    pwd1 = request.form.get('password1')
    pwd2 = request.form.get('password2')
    if pwd1 == pwd2:
        pwd_hash = generate_password_hash(pwd1)
        new_pilot = Pilot(name=request.form.get('name'), pwd_hash=pwd_hash, role=request.form.get('role'))

        db.session.add(new_pilot)
        db.session.commit()

        flash("Added new Pilot!", 'success')
    else:
        flash("Passwords dont match!", 'danger')
    return redirect(url_for('webinterface.pilots'))

@webinterface.route("/pilots/edit", methods = {'POST'})
@login_required
def edit_pilot():
    failed = False
    id = int(request.form.get('id'))
    if Pilot.exists(id=id):
        pilot = Pilot.query.filter_by(id=id).first()
        new_pwd = bool(request.form.get('changePwd'))
        if new_pwd:
            pwd1 = request.form.get('password1')
            pwd2 = request.form.get('password2')
            if pwd1 == pwd2:
                pilot.pwd_hash = generate_password_hash(pwd1)
            else:
                flash("Passwords dont match!", 'danger')
                failed = True
        if not failed:
            pilot.name = request.form.get('name')
            if id != current_user.id:
                pilot.role = request.form.get('role')

            db.session.commit()
            flash("Saved Pilot Settings!", 'success')
    else:
        flash("Pilot dose not exist!", 'danger')
    
    return redirect(url_for('webinterface.pilots'))

@webinterface.route("/pilots", methods = {'GET'})
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
        return redirect(url_for('webinterface.agents'))