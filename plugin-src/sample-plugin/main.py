# Importing mixin super class
from pplib.plugins.api import *

# Importing needed classes, functions and variables
from pplib.service import serviceConf

# Creating a Mixins class that holds all mixin functions
#
# The @Mixin decorator maps all functions inside the class to there name in string form
# This function map can be accessed as self.functions
#
# It also creates a __init__ with arguments:
#       - meta (holds metadata dict)
#       - logging(default True, enables logging)
#
# Each Mixin Function hase to have the name of the mixin it wants to access.
# They also have to have a args (dict) argument where they can get arguments form.
# 
# INFO: This class is Required for the Plugin to run
@Mixin
class Mixins():
    def core(self, args = dict()):
        """
        Core mixin that is called just befor the Flask App is started
        - return:
            True if execution was succesfull, else return False
        """
        global serviceConf

        self.log(f"Setting {self.Color.Bright.Magenta}service.online{self.Color.White} to False")
        
        serviceConf["online"] = False
        return True
        