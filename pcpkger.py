from pilotica.components.generation import ComponentPKGCompiler
from pilotica.console import Color, Logger
import argparse
import yaml
import os

"""
This is a tool to pack Pilotica-Component Source directorys
into Pilotica-Component-Packages, that can be used like
Plugin packages.
"""

def get_args():
    parser = argparse.ArgumentParser(
        prog='Pilotica-Component Packager',
        description='Packs Pilotica-Component Source directorys into Pilotica-Component-Packages'
    )

    parser.add_argument(
        '--src',
        default=None,
        required=False
    )
    parser.add_argument(
        '-o', '--output',
        help='Output directory',
        default=None,
        required=False
    )
    parser.add_argument(
        '-a', '--auto',
        help='Automaticly build all Component-Packages requirred to run Pilotica',
        required=False,
        action='store_true'
    )

    return parser.parse_args()

if __name__ == "__main__":
    logger = Logger()

    args = get_args()

    PCPKG_Compiler = ComponentPKGCompiler()

    start_msg = f"Started Pilotica-Component Packager in '{'auto' if args.auto else 'manual'}' mode!"
    logger.custom(start_msg, {Color.Bright.Magenta}, True, str())

    if args.auto:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pkgsrc')
        if args.output == None:
            dst_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'instance/components')
        else:
            dst_folder = args.output

        if not os.path.isdir(dst_folder):
                os.makedirs(dst_folder)
        
        sub_folders = [os.path.join(path, name) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        for src_folder in sub_folders:
            logger.info(f"Generating Component-Package for: {src_folder}")
            
            PCPKG_Compiler.validate(src_folder)

            with open(os.path.join(src_folder, "meta.yaml"), 'r') as metayaml:
                meta = yaml.safe_load(metayaml)

            PCPKG_Compiler.compile(src_folder, os.path.join(dst_folder, meta["alias"]+'.pcpkg'))
    else:
        src_folder = args.src
        if src_folder == None:
            logger.error("--src is required in manual mode!")
            parser.print_usage()
            exit(-1)

        if args.output == None:
            dst_folder = os.getcwd()
        else:
            dst_folder = args.output

        if not os.path.isdir(dst_folder):
                os.makedirs(dst_folder)

        logger.info(f"Generating Component-Package for: {src_folder}")
        
        PCPKG_Compiler.validate(src_folder)

        with open(os.path.join(src_folder, "meta.yaml"), 'r') as metayaml:
            meta = yaml.safe_load(metayaml)

        PCPKG_Compiler.compile(src_folder, os.path.join(dst_folder, meta["alias"]+'.pcpkg'))
    print()