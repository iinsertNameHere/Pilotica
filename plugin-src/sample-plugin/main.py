# Importing plugin api
from pplib.plugin.api import *

# Importing needed classes, functions and variables
from pplib.service import serviceConf

# Creating a Mixins class that holds all mixin functions
# The @Mixin initializes all mixin functionality
#
# Each Mixin Function has to have the name of the mixin it wants to access.
# 
# INFO: This class is Required for the Plugin to run
@Mixin
class Mixins():
    def core(self, **kwargs):
        """
        Core mixin that is called just befor the Flask App is started
        - return:
            True if execution was succesfull, else return False
        """
        global serviceConf

        # self.log only outputs the given msg to the console if logging is enabled
        self.log(f"Setting {self.Color.Bright.Magenta}service.online{self.Color.White} to False")
        serviceConf["online"] = False
        
        return True
        