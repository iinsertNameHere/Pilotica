from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
import json

db = SQLAlchemy()

class Pilot(UserMixin, db.Model):
    __tablename__ = "pilots"
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(20), nullable=False, unique=True)
    pwd_hash      = db.Column(db.Text, nullable=False)
    role          = db.Column(db.String(8), nullable=False) # OBSERVER, ADMIN, OPERATOR

    def exists(name: str = None, id: int = None):
        if name == None and id == None:
            return False
    
        if name != None:
            pilot = Pilot.query.filter_by(name=name).first()
        else:
            pilot = Pilot.query.filter_by(id=id).first()
        
        return pilot != None
    
    def jsonify(self, asDict=False):
        dict_repr = {
            "id": self.id,
            "name": self.name,
            "pwd_hash": self.pwd_hash,
            "role": self.role,
        }
        if not asDict:
            return json.dumps(dict_repr)
        else:
            return dict_repr

class Agent(db.Model):
    __tablename__ = "agents"
    id            = db.Column(db.Integer, primary_key=True)
    uuid          = db.Column(db.String(60), nullable=False, unique=True)
    hostname      = db.Column(db.String(64), nullable=False)
    beacon        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tasks         = db.relationship('Task', backref='agent', lazy=True)
    
    def clear_tasks(self):
        tasks = Task.query.filter_by(agent_id=self.id).all()
        for task in tasks:
            db.session.delete(task)
        db.session.commit()

    def clear_allTasks():
        agents = Agent.query.all()
        for agent in agents:
            agent.clear_tasks()

    def get_by_uuid(uuid: str):
        return Agent.query.filter_by(uuid=uuid).first()

    def get_nextTask(uuid: str):
        agent = Agent.query.filter_by(uuid=uuid).first()
        if agent is None:
            return None
        task = Task.query.filter_by(agent_id=agent.id).filter_by(fired=False).first()
        if task is None:
            return None
        task.fire()
        return task

    def update_beacon(uuid: str):
        Agent.query.filter_by(uuid=uuid).first().beacon = datetime.utcnow()
        db.session.commit()

    def exists(uuid: str = None, id: int = None):
        if uuid == None and id == None:
            return False
    
        if uuid != None:
            agent = Agent.query.filter_by(uuid=uuid).first()
        else:
            agent = Agent.query.filter_by(id=id).first()
        
        return agent != None

    def delete(id: int):
        agent = Agent.query.filter_by(id=id).first()
        agent.clear_tasks()
        db.session.delete(agent)
        db.session.commit()

    def delete_all():
        tasks = Task.query.all()
        for task in tasks:
            db.session.delete(task)

        agents = Agent.query.all()
        for agent in agents:
            db.session.delete(agent)

        db.session.commit()

    def __repr__(self):
        return "Agent{" + f"id: {self.id}, uuid: {self.uuid}" + "}"

    def jsonify(self, asDict=False):
        dict_repr = {
            "id": self.id,
            "uuid": self.uuid,
            "hostname": self.hostname,
            "beacon": str(self.beacon),
            "task_count": len(Task.query.filter_by(agent_id=self.id).all())
        }
        if not asDict:
            return json.dumps(dict_repr)
        else:
            return dict_repr

class Task(db.Model):
    __tablename__ = "tasks"
    id       = db.Column(db.Integer, primary_key=True)
    file     = db.Column(db.String(64), nullable=False)
    args     = db.Column(db.Text, nullable=True)
    fired    = db.Column(db.Boolean, nullable=False, default=False)
    verbose  = db.Column(db.Boolean, nullable=False, default=False)
    reply    = db.Column(db.Text, nullable=True, default=None)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)

    def delete(id: int):
        task = Task.query.filter_by(id=id).first()
        db.session.delete(task)
        db.session.commit()

    def get_by_id(task_id: int):
        return Task.query.filter_by(id=task_id).first()

    def fire(self):
        self.fired = True
        db.session.commit()
    
    def set_reply(self, reply: str):
        self.reply = reply
        db.session.commit()

    def get_reply(self):
        return self.reply

    def jsonify(self):
        dict_repr = {
            "id": self.id,
            "file": self.file,
            "args": json.loads(self.args),
            "verbose": self.verbose
        }
        return json.dumps(dict_repr)