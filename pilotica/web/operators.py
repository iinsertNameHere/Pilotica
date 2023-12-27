class __operator_roles__:
    def __init__(self):
        # r = read
        # w = write
        # c = configure
        self.OBSERVER = {"name": "OBSERVER", "rights": ['r']}
        self.OPERATOR = {"name": "OPERATOR", "rights": ['r', 'w']}
        self.ADMIN    = {"name": "ADMIN", "rights": ['r', 'w', 'c']}

OperatorRoles = __operator_roles__()
