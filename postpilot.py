from pplib import setup_app, plugin_manager
from pplib.console import Color

VERSION = "v1.0"

host = "127.0.0.1"
port = 4444

app, config = setup_app(__name__)

if __name__ == "__main__":
    if not config.pilot.get("DEBUG"):
        print(f"{Color.Bright.Blue}::{Color.White} Runing PostPilot {VERSION}"+Color.Reset)
        print(f"{Color.Bright.Blue}::{Color.White} SECRET_KEY: {Color.Bright.Magenta}{app.config['SECRET_KEY']}"+Color.Reset)
    else:
        print(f" * Runing PostPilot {VERSION}")
        print(f" * Secret Key: {app.config['SECRET_KEY']}")

    # Handling Core Plugins
    for index in plugin_manager.get("core"):
        plugin_manager.plugins["all"][index].mixins.core()

    app.run(host, port, debug=config.pilot.get("DEBUG"), threaded=True)