from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Agent(db.Model):
    __tablename__ = "agents"
    id            = db.Column(db.Integer, primary_key=True)
    hostname      = db.Column(db.String(64), nullable=False, unique=True)
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

    def get_by_hostname(hostname: str):
        return Agent.query.filter_by(hostname=hostname).first()

    def get_nextTask(hostname: str):
        agent = Agent.query.filter_by(hostname=hostname).first()
        if agent is None:
            return None
        task = Task.query.filter_by(agent_id=agent.id).filter_by(fired=False).first()
        if task is None:
            return None
        task.fire()
        return task

    def update_beacon(hostname: str):
        Agent.query.filter_by(hostname=hostname).first().beacon = datetime.utcnow()
        db.session.commit()

    def exists(hostname: str = None, id: int = None):
        if hostname == None and id == None:
            return False
    
        if hostname != None:
            agent = Agent.query.filter_by(hostname=hostname).first()
        else:
            agent = Agent.query.filter_by(id=id).first()
        
        return agent != None

    def delete_all():
        tasks = Task.query.all()
        for task in tasks:
            db.session.delete(task)

        agents = Agent.query.all()
        for agent in agents:
            db.session.delete(agent)

        db.session.commit()

class Task(db.Model):
    __tablename__ = "tasks"
    id       = db.Column(db.Integer, primary_key=True)
    file     = db.Column(db.String(64), nullable=False)
    args     = db.Column(db.Text, nullable=True)
    fired    = db.Column(db.Boolean, nullable=False, default=False)
    verbose  = db.Column(db.Boolean, nullable=False, default=False)
    reply    = db.Column(db.Text, nullable=True, default=None)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)

    def get_by_id(task_id: int):
        return Task.query.filter_by(id=task_id).first()

    def fire(self):
        Task.query.filter_by(id=self.id).first().fired = True
        db.session.commit()
    
    def set_reply(self, reply: str):
        Task.query.filter_by(id=self.id).first().reply = reply
        db.session.commit()

    def get_reply(self):
        return Task.query.filter_by(id=self.id).first().reply

    def jsonify(self):
        dict_repr = {
            "id": self.id,
            "file": self.file,
            "args": json.loads(self.args),
            "verbose": self.verbose
        }
        return json.dumps(dict_repr)