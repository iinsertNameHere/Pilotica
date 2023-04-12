from ..console import Color

# Mixin class decorator
def Mixin(cls):
    cls.Color = Color

    def log(self, msg: str):
        if self.logging:
            print(f"{self.Color.Bright.Blue}::{self.Color.White} {msg}"+self.Color.Reset)
    cls.log = log

    def init(self, meta: dict, logging=True):
        self.logging = True
        self.meta = meta
        self.log(f"Loaded Plugin {self.Color.Bright.Magenta}{meta['alias']} v{meta['version']}")
        self.logging = logging
    cls.__init__ = init
    
    return cls