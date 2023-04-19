from pilotica import setup_app, component_manager
from pilotica.components.decorators import *
from pilotica.console import Color
from flask import send_from_directory
import pilotica.settings as ps

import argparse

import os

VERSION = "v1.0"

host = "127.0.0.1"
port = 4444

app, config = (None, None)

@EnableComponents(globals(), "core")
def main():
    global app, config
    app, config = setup_app(__name__)

    if not config.pilotica.get("DEBUG"):
        if os.name == 'nt':
            os.system("set FLASK_ENV=production")
        else:
            os.system("export FLASK_ENV=production")
        print(f"{Color.Bright.Yellow}::{Color.White} Runing Pilotica {VERSION}"+Color.Reset)
        print(f"{Color.Bright.Yellow}::{Color.White} secret key: {Color.Bright.Magenta}{app.config['SECRET_KEY']}"+Color.Reset)
        print(f"{Color.Bright.Yellow}::{Color.White} Running on {Color.Bright.Yellow}http://{host}:{port}"+Color.Reset)
        print(Color.Blue+"Press CTRL+C to quit\n"+Color.Reset)
    else:
        print(f" * Runing Pilotica {VERSION}")
        print(f" * Secret Key: {app.config['SECRET_KEY']}")
        print(f" * Running on {Color.Bright.Yellow}http://{host}:{port}"+Color.Reset)

    HANDLE_PCPKGS

    app.run(host, port, debug=config.pilotica.get("DEBUG"), threaded=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Pilotica C2 Server')

    parser.add_argument('--no-components', help='Starts Pilotica without loading Component-Packages',
        required=False, action='store_true', default=False)

    args = parser.parse_args()

    ps.no_components = args.no_components

    main()