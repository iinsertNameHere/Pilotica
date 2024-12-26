from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy.orm import declarative_base
from bcrypt import hashpw, gensalt, checkpw
from .premissions import Premissions, Premission
from .identicon import generate_identicon
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from secrets import token_urlsafe
from uuid import uuid4 as rand_uuid

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

# Database setup
DATABASE_URL = "sqlite:///./pilotica.db"  # or any other DB URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    except OperationalError:
        print("Database connection error.")
    finally:
        db.close()
