# Importing Component-Package api
from pilotica.components.api import *

# Importing needed classes, functions and variables
from base64 import urlsafe_b64encode as base64encode, urlsafe_b64decode as base64decode
import pilotica.web.transport as tp

@Scopes
class Scopes():
    def transport(self, **kwargs):
        def dump(self):
            return base64encode(self.data.encode()).decode()
        tp.Transport.dump = dump

        def load(self):
            return base64decode(self.data.encode()).decode()
        tp.Transport.load = load

        M = self.Color.Bright.Magenta
        W = self.Color.White
        self.log(f"{self.meta['alias']}: {M}Transport.dump{W} and {M}Transport.load{W} where overwritten")

        return kwargs["data"]