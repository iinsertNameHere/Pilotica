class __pilot_roles__:
    def __init__(self):
        # r = read
        # w = write
        # c = configure
        self.OBSERVER = {"name": "OBSERVER", "rights": ['r']}
        self.OPERATOR = {"name": "OPERATOR", "rights": ['r', 'w']}
        self.ADMIN    = {"name": "ADMIN", "rights": ['r', 'w', 'c']}

PilotRoles = __pilot_roles__()
