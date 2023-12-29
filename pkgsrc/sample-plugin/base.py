# Importing Component-Package api
from pilotica.components.api import *

# Importing needed classes, functions and variables
from pilotica.web.service import serviceConf

# Creating a Scopes class that holds all Scope functions
# The @Scopes initializes all Scope functionality
#
# Each Scope function has to have the name of the scope it wants to access.
# 
# INFO: This class is Required for the Component-Packages to run
@Scopes
class Scopes():
    def core(self, **kwargs):
        """
        Core scope function that is called just befor the Flask App is started
        - return:
            True if execution was succesfull, else return False
        """
        global serviceConf

        # self.log only outputs the given msg to the console if logging is enabled
        self.log(f"Setting {self.Color.Bright.Magenta}service.online{self.Color.White} to False")
        serviceConf["online"] = False
        
        return True
        