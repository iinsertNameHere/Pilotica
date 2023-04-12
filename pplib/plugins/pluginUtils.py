from os.path import join as join_path, isfile, isdir, basename, abspath, dirname
from os import chdir
from zipfile import PyZipFile, ZipFile
from pathlib import Path
import sys
from zipimport import zipimporter
import yaml
import inspect

currentdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
parentdir = dirname(currentdir)
sys.path.insert(0, parentdir) 

from console import Color

class PluginCompiler:
    def validate(folder: str):        
        if not isdir(folder):
            print(Color.Red+f"ERROR: {folder} is not a folder!"+Color.Reset)
            exit(-1)

        if not isfile(join_path(folder, "meta.yaml")):
            print(Color.Red+f"ERROR: missing medatada: meta.yaml"+Color.Reset)
            exit(-1)

        if not isfile(join_path(folder, "main.py")):
            print(Color.Red+f"ERROR: missing main file: main.py"+Color.Reset)
            exit(-1)

        return True

    def compile(folder: str):
        plugin_path: str = Path(folder).stem + ".ppkg"

        with PyZipFile(plugin_path, mode='w') as pyzfile:
            pyzfile.writepy(join_path(folder, "main.py"))
            pyzfile.write(join_path(folder, "meta.yaml"), 'meta.yaml')

class Plugin:
    def __init__(self, instance_path: str, plugin_name, logging=True):
        self.path = join_path(instance_path, "plugins", plugin_name+".ppkg")
        self.name = plugin_name

        if not isfile(self.path):
            print(Color.Red+f"ERROR: Plugin file missing: {self.path}"+Color.Reset)
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
            "transport": list()
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

if __name__ == "__main__":
    try:
        folder = sys.argv[1]
    except:
        print(f"Usage: {sys.argv[0]} folder")
        exit(-1)

    PluginCompiler.validate(folder)
    PluginCompiler.compile(folder)