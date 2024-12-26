from uuid import uuid4 as rand_uuid

class Premission:
    def __init__(self, name: str, uuid: str=None):
        self.name = name
        self.uuid = uuid

        if self.uuid == None:
            self.uuid = rand_uuid()

    def __repr__(self):
        return f"<{self.name}:{self.uuid}>"

    def to_string(self):
        return f"<{self.name}:{self.uuid}>"

    def to_json(self) -> tuple:
        return (self.name, self.uuid)

    def equals(self, p):
        return (self.name == p.name and self.uuid == p.uuid)

    def from_string(s: str):
        parts = s.strip().replace("<", "").replace(">", "").split(":")
        if len(parts) < 2:
            raise ValueError("Not a valid string repr of Premission")
        
        return Premission(parts[0], parts[1])


class Premissions:
    Admin = Premission("Admin", "a7c22f63-19be-4104-afa2-0b7a496f5fc2")
    Configurator = Premission("Configurator", "a0ce7115-7f81-4763-bec6-8bb9f61be6e0")
    Operator = Premission("Operator", "e27c36a2-5fa3-47cf-926b-64ad29ee85ae")
    Spectator = Premission("Spectator", "dde2fdf0-b359-428f-b5de-7bda8a8731b9")

    def to_json() -> dict:
        return {
            "Admin": Premissions.Admin.to_json(),
            "Configurator": Premissions.Configurator.to_json(),
            "Operator": Premissions.Operator.to_json(),
            "Spectator": Premissions.Spectator.to_json()
        }
