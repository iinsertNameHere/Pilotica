from os.path import join as join_path, isfile, dirname, abspath
from zipimport import zipimporter
from zipfile import ZipFile
import inspect
import yaml
import sys

currentdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
parentdir = dirname(currentdir)
sys.path.insert(0, parentdir) 

from console import Color

COMPONENTPGKS_EXT = ".pcpkg"

class Component:
    def __init__(self, instance_path: str, name, logging=True):
        self.path = join_path(instance_path, "components", name+COMPONENTPGKS_EXT)
        self.name = name

        if not isfile(self.path):
            print(Color.Red+f"::{Color.White} Component-Package missing: {self.path}"+Color.Reset)
            exit(-1)
        
        importer = zipimporter(self.path)
        self.module = importer.load_module("base")

        with ZipFile(self.path).open("meta.yaml") as metayaml:
            self.meta = yaml.safe_load(metayaml)

        self.scopes = self.module.Scopes(self.meta, logging)

class ComponentManager:
    def __init__(self):
        self.components = {
            "all": list(),
            "core": list(),
            "transport": list(),
            "service": list()
        }

    def add(self, component: Component):
        self.components.get("all").append(component)
        component_index = len(self.components.get("all"))-1

        for scope_name in component.meta.get("scopes"):
            if scope_name in self.components.keys() and scope_name != "all":
                self.components.get(scope_name).append(component_index)
            else:
                print(Color.Red+f"::{Color.White} Unknown Component-Package scope: {scope_name}"+Color.Reset)
                exit(-1)

    def get_byScope(self, scope_name: str):
        if scope_name in self.components.keys():
            return self.components.get(scope_name)
        else:
            return None