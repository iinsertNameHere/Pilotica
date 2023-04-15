# Importing plugin api
from pilotica.plugin.api import *

# Importing needed classes, functions and variables
from uuid import uuid4

@Mixin
class Mixins():
    def service(self, **kwargs):
        service_dict = kwargs["service_dict"]

        # Generate a random uuid to test the service api with
        self.log(f"Random test agent uuid {self.Color.Bright.Magenta}{uuid4()}\n")
        
        return True
        