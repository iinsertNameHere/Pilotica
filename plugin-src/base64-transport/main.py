# Importing mixin super class
from pplib.plugins.api import *

# Importing needed classes, functions and variables
from base64 import urlsafe_b64encode as base64encode, urlsafe_b64decode as base64decode
import pplib.transport as tp

@Mixin
class Mixins():
    def transport(self, args: dict = dict()):
        def dump(self):
            return base64encode(self.data.encode()).decode()
        tp.Transport.dump = dump

        def load(self):
            return base64decode(self.data.encode()).decode()
        tp.Transport.load = load

        M = self.Color.Bright.Magenta
        W = self.Color.White
        self.log(f"{self.meta['alias']}: {M}Transport.dump{W} and {M}Transport.load{W} where overwritten")

        return True
        