from os.path import join as join_path, isfile, isdir, dirname, abspath
from zipfile import PyZipFile, ZipFile
import importlib.util as importutil
from cerberus import Validator
from pathlib import Path
from os import chdir
import inspect
import yaml
import sys

currentdir = dirname(abspath(inspect.getfile(inspect.currentframe())))
parentdir = dirname(currentdir)
sys.path.insert(0, parentdir) 

from console import Color

class PluginCompiler:
    def __init__(self):
        self.meta_validator = Validator(
            {
                'name': {
                    'type': 'string',
                    'required': True,
                    'minlength': 1
                },
                'alias': {
                    'type': 'string',
                    'required': True,
                    'minlength': 1
                },
                'creator': {
                    'type': 'string',
                    'required': True,
                    'minlength': 1
                },
                'version': {
                    'type': 'string',
                    'required': True,
                    'regex': '^\\d+\\.\\d+\\.\\d+$'
                },
                'description': {
                    'type': 'string',
                    'required': True,
                    'minlength': 1
                },
                'mixins': {
                    'type': 'list',
                    'required': True,
                    'minlength': 1,
                    'schema': {
                        'type': 'string',
                        'minlength': 1
                    }
                }
            }
        )

    def validate(self, folder: str):
        """
        Validates the directory structure and code structure of a given plugin src folder.

        @param folder: folder to validate
        @return: True if valid else False
        """    

        # Validating folder structure 
        if not isdir(folder):
            print(Color.Red+f"ERROR: {folder} is not a folder!"+Color.Reset)
            exit(-1)

        if not isfile(join_path(folder, "meta.yaml")):
            print(Color.Red+f"ERROR: missing medatada: meta.yaml"+Color.Reset)
            exit(-1)

        if not isfile(join_path(folder, "main.py")):
            print(Color.Red+f"ERROR: missing main file: main.py"+Color.Reset)
            exit(-1)

        # Validating meta.yaml
        try:
            with open(join_path(folder, "meta.yaml"), "r") as f:
                meta = yaml.safe_load(f)
        except yaml.YAMLError:
            print(Color.Red+f"ERROR: meta.yaml test load failed!"+Color.Reset)
            exit(-1)
        
        if not self.meta_validator.validate(meta):
            for error in self.meta_validator.errors:
                print(Color.Red+f"ERROR: Failed to validate '{error}' in meta.yaml"+Color.Reset)
            exit(-1)

        spec = importutil.spec_from_file_location("main", join_path(folder, "main.py"))
        main = importutil.module_from_spec(spec)
        sys.modules["main"] = main
        spec.loader.exec_module(main)

        if not "Mixins" in main.__dir__():
            print(Color.Red+f"ERROR: main.py is missing Mixin class!"+Color.Reset)
            exit(-1)

        if not getattr(main.Mixins, "__mixin_deco__", False):
            print(Color.Red+f"ERROR: Mixin class is missing the @Mixin decorator!"+Color.Reset)
            exit(-1)

        return True

    def compile(self, src_folder: str, dst_folder: str):
        plugin_path: str = join_path(dst_folder, Path(src_folder).stem + ".ppkg")

        with PyZipFile(plugin_path, mode='w') as pyzfile:
            pyzfile.writepy(join_path(src_folder, "main.py"))
            pyzfile.write(join_path(src_folder, "meta.yaml"), "meta.yaml")