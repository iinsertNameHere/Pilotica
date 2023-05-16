# Importing Component-Package api
from pilotica.components.api import *

# Importing needed classes, functions and variables
from base64 import urlsafe_b64encode as base64encode, urlsafe_b64decode as base64decode

@Scopes
class Scopes():
    def transport(self, **kwargs):
        if kwargs["direction"] == "out":
            return base64encode(kwargs["data"].encode()).decode()
        elif kwargs["direction"] == "in":
            return base64decode(kwargs["data"].encode()).decode()
        else:
            return kwargs["data"]