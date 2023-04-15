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

class Plugin:
    def __init__(self, instance_path: str, plugin_name, logging=True):
        self.path = join_path(instance_path, "plugins", plugin_name+".ppkg")
        self.name = plugin_name

        if not isfile(self.path):
            print(Color.Red+f"::{Color.White} Plugin file missing: {self.path}"+Color.Reset)
            exit(-1)
        
        importer = zipimporter(self.path)
        self.module = importer.load_module("main")

        with ZipFile(self.path).open("meta.yaml") as metayaml:
            self.meta = yaml.safe_load(metayaml)

        self.mixins = self.module.Mixins(self.meta, logging)

class PluginManager:
    def __init__(self):
        self.plugins = {
            "all": list(),
            "core": list(),
            "transport": list(),
            "service": list()
        }

    def add(self, plugin: Plugin):
        self.plugins["all"].append(plugin)
        plugin_index = len(self.plugins["all"])-1

        for mixin_name in plugin.meta["mixins"]:
            if mixin_name in self.plugins.keys() and mixin_name != "all":
                self.plugins[mixin_name].append(plugin_index)

    def get(self, mixin_name: str):
        if mixin_name in self.plugins.keys():
            return self.plugins[mixin_name]
        else:
            return None