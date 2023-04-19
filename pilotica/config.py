import yaml
from .console import Color
from flask import Flask
from os.path import join as join_path
from shutil import copyfile

import pilotica.settings as ps

class Config:
    def __init__(self, instance_path: str, file_path: str):
        self.instance_path = instance_path
        self.path = file_path
        self.raw = dict()
        self.pilotica = dict()
        self.component_list: list[dict] = list()

    def create(self):
        origin = join_path(self.instance_path, 'config', 'origin.yaml')
        path = join_path(self.instance_path, self.path)
        try:
            copyfile(origin, path)
        except:
            print(f"{Color.Red}::{Color.White} Failed to create Config!"+Color.Reset)
            exit(-1)  
        
        self.load()

    def load(self):
        path = join_path(self.instance_path, self.path)
        try:
            with open(path, "r") as f:
                self.raw = yaml.safe_load(f)
        except:
            print(f"{Color.Red}::{Color.White} Failed to load Config!"+Color.Reset)
            exit(-1)

        not_optional = [("DEBUG", bool), ("API_LOGGING", bool), ("secret_key", str)]

        if not "pilotica" in self.raw.keys():
            print(f"{Color.Red}::{Color.White} The field pilotica is not optional!"+Color.Reset)
            exit(-1)
        else:
            self.pilotica = self.raw["pilotica"]

        for field in not_optional:
            if not field[0] in self.pilotica.keys():
                print(f"{Color.Red}::{Color.White} The field pilotica.{field[0]} is not optional!"+Color.Reset)
                exit(-1)
            if not field[1] is type(self.pilotica[field[0]]):
                print(f"{Color.Red}::{Color.White} The field pilotica.{field[0]} has not the expected type!"+Color.Reset)
                exit(-1)

        if not ps.no_components:
            if "components" in self.raw.keys():
                self.component_list = self.raw["components"]
            else:
                print(f"{Color.Yellow}The field pilotica.components is optional and not set. This my be an error,\nPlease check you config!\n\nTo suppress this warning in the future when not using component pkgs, please use the '--no-components' argument.\n"+Color.Reset)
        
            for i, component in enumerate(self.component_list):
                for key in ["alias", "logging"]:
                    if not key in component.keys():
                        print(f"{Color.Red}::{Color.White} item {i+1} from components list in file '{self.path}' is missing field: {key}"+Color.Reset)
                        exit(-1)

        
        
