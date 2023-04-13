from .plugin.decorators import *

plugin_manager = None

class Transport:
    @EnableMixins(globals(), "transport", args=["data"])
    def __init__(self, data: str):
        HANDLE_MIXINS
        self.data = plugin_returns[0]
    
    def dump(self):
        return self.data

    def load(self):
        return self.data