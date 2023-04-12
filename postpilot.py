from lib import setup_app
from lib.console import Color

VERSION = "v1.0"
DEBUG = True
API_LOGGING = True

host = "127.0.0.1"
port = 4444

app = setup_app(__name__, api_logging=API_LOGGING)

if __name__ == "__main__":
    if not DEBUG:
        print(f"{Color.Bright.Blue}::{Color.White} Runing PostPilot {VERSION}"+Color.Reset)
        print(f"{Color.Bright.Blue}::{Color.White} SECRET_KEY: {Color.Bright.Magenta}{app.config['SECRET_KEY']}"+Color.Reset)
    else:
        print(f" * Runing PostPilot {VERSION}")
        print(f" * Secret Key: {app.config['SECRET_KEY']}")

    app.run(host, port, debug=DEBUG, threaded=True)