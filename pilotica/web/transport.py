from ..components.decorators import *

class Transport:
    @EnableComponents(globals(), "transport", args=["data"])
    def __init__(self, data: str):
        HANDLE_PCPKGS
        self.data = component_returns[0]
    
    def dump(self):
        return self.data

    def load(self):
        return self.data