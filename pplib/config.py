import yaml
from .console import Color
from flask import Flask
from os.path import join as join_path
from shutil import copyfile

class Config:
    def __init__(self, instance_path: str, file_path: str):
        self.instance_path = instance_path
        self.path = file_path
        self.raw = dict()
        self.pilot = dict()
        self.plugin_list = list()

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
        #try:
        with open(path, "r") as f:
            self.raw = yaml.safe_load(f)
        #except:
        #    print(f"{Color.Red}::{Color.White} Failed to load Config!"+Color.Reset)
        #    exit(-1)

        not_optional = [("DEBUG", bool), ("API_LOGGING", bool)]

        if not "pilot" in self.raw.keys():
            print(f"{Color.Red}::{Color.White} The field pilot is not optional!"+Color.Reset)
            exit(-1)
        else:
            self.pilot = self.raw["pilot"]

        for field in not_optional:
            if not field[0] in self.pilot.keys():
                print(f"{Color.Red}::{Color.White} The field pilot.{field[0]} is not optional!"+Color.Reset)
                exit(-1)
            if not field[1] is type(self.pilot[field[0]]):
                print(f"{Color.Red}::{Color.White} The field pilot.{field[0]} has not the expected type!"+Color.Reset)
                exit(-1)

        if not "plugins" in self.raw.keys():
            self.plugin_list = []
        else:
            self.plugin_list = self.raw["plugins"]

        
        
