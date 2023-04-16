from cerberus import Validator
import yaml

pilot_validator = Validator({
    'name': {'type': 'string', 'required': True, "maxlength": 20},
    'password': {'type': 'string', 'required': True},
    'role': {'type': 'string', 'allowed': ['OBSERVER', 'OPERATOR', 'ADMIN'], 'required': True},
})

def validate(file_path: str):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError:
            print(Color.Red+f"ERROR: {file_path} load failed!"+Color.Reset)
            exit(-1)
    return pilot_validator.validate(data)

class __pilot_roles__:
    def __init__(self):
        # r = read
        # w = write
        # c = configure
        self.OBSERVER = {"name": "OBSERVER", "rights": ['r']}
        self.OPERATOR = {"name": "OPERATOR", "rights": ['r', 'w']}
        self.ADMIN    = {"name": "ADMIN", "rights": ['r', 'w', 'c']}

PilotRoles = __pilot_roles__()
