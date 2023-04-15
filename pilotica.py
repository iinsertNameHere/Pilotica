from pilotica import setup_app, plugin_manager
from pilotica.plugin.decorators import *
from pilotica.console import Color

import os

VERSION = "v1.0"

host = "127.0.0.1"
port = 4444

app, config = setup_app(__name__)

@EnableMixins(globals(), "core")
def main():
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

    HANDLE_MIXINS

    app.run(host, port, debug=config.pilotica.get("DEBUG"), threaded=True)

if __name__ == "__main__":
    main()