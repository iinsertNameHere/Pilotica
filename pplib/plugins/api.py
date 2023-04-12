# Mixin class decorator
def Mixin(cls): 
    def init(self, meta: dict, logging=True):
        self.logging = logging
        self.meta = meta
        if logging: print(f"PLUGIN: Loaded {meta['name']} ({meta['alias']}={meta['version']})")
    cls.__init__ = init
    
    return cls