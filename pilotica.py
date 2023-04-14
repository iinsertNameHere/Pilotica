from pplib import setup_app, plugin_manager
from pplib.plugin.decorators import *
from pplib.console import Color

VERSION = "v1.0"

host = "127.0.0.1"
port = 4444

app, config = setup_app(__name__)

@EnableMixins(globals(), "core")
def main():
    if not config.pilotica.get("DEBUG"):
        print(f"{Color.Bright.Blue}::{Color.White} Runing Pilotica {VERSION}"+Color.Reset)
        print(f"{Color.Bright.Blue}::{Color.White} SECRET_KEY: {Color.Bright.Magenta}{app.config['SECRET_KEY']}"+Color.Reset)
    else:
        print(f" * Runing Pilotica {VERSION}")
        print(f" * Secret Key: {app.config['SECRET_KEY']}")

    HANDLE_MIXINS

    app.run(host, port, debug=config.pilotica.get("DEBUG"), threaded=True)

if __name__ == "__main__":
    main()