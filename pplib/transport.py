plugin_manager = None

class Transport:
    def __init__(self, data: str):
        self.data = data
        # Handling Transport Plugins
        for index in plugin_manager.get("transport"):
            plugin_manager.plugins["all"][index].mixins.transport()
    
    def dump(self):
        return self.data

    def load(self):
        return self.data