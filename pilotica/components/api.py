from ..console import Color

# Scopes class decorator
def Scopes(cls):
    cls.__scopes_deco__ = True
    cls.Color = Color

    def log(self, msg: str):
        if self.logging:
            print(f"{self.Color.Bright.Blue}::{self.Color.White} {msg}"+self.Color.Reset)
    cls.log = log

    def init(self, meta: dict, logging=True):
        self.logging = True
        self.meta = meta
        self.log(f"Loaded Component-Package {self.Color.Bright.Magenta}{meta['alias']} v{meta['version']}")
        self.logging = logging
    cls.__init__ = init
    
    return cls