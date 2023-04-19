from pilotica.components.generation import ComponentPKGCompiler
from pilotica.console import Color
import os
import argparse
import yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='Pilotica-Component Packager',
                    description='Packs Pilotica-Component Source directorys into Pilotica-Component-Packages')

    parser.add_argument('--src', default=None, required=False)
    parser.add_argument('-o', '--output', help='Output directory',
        default=None, required=False)
    parser.add_argument('-a', '--auto', help='Automaticly build all Component-Packages requirred to run Pilotica',
        required=False, action='store_true', )

    args = parser.parse_args()

    PCPKG_Compiler = ComponentPKGCompiler()
    
    print(f"{Color.Bright.Magenta}Started Pilotica-Component Packager in {'auto' if args.auto else 'manual'} mode!"+Color.Reset)

    if args.auto:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'component-src')
        if args.output == None:
            dst_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'instance/components')
        else:
            dst_folder = args.output

        if not os.path.isdir(dst_folder):
                os.makedirs(dst_folder)
        
        sub_folders = [os.path.join(path, name) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        for src_folder in sub_folders:
            print(f"{Color.Bright.Blue}::{Color.White} Generating Component-Package for: {src_folder}"+Color.Reset)
            
            PCPKG_Compiler.validate(src_folder)

            with open(os.path.join(src_folder, "meta.yaml"), 'r') as metayaml:
                meta = yaml.safe_load(metayaml)

            PCPKG_Compiler.compile(src_folder, os.path.join(dst_folder, meta["alias"]+'.pcpkg'))
    else:
        src_folder = args.src
        if src_folder == None:
            print(f"{Color.Red}::{Color.White} --src is required in manual mode!"+Color.Reset)
            parser.print_usage()
            exit(-1)

        if args.output == None:
            dst_folder = os.getcwd()
        else:
            dst_folder = args.output

        if not os.path.isdir(dst_folder):
                os.makedirs(dst_folder)

        print(f"{Color.Bright.Blue}::{Color.White} Generating Component-Package for: {src_folder}"+Color.Reset)
        
        PCPKG_Compiler.validate(src_folder)

        with open(os.path.join(src_folder, "meta.yaml"), 'r') as metayaml:
            meta = yaml.safe_load(metayaml)

        PCPKG_Compiler.compile(src_folder, os.path.join(dst_folder, meta["alias"]+'.pcpkg'))
    print()