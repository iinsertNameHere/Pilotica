from lib import setup_app
from lib.console import Color

VERSION = "v1.0"

host = "127.0.0.1"
port = 4444

app, db = setup_app()

if __name__ == "__main__":
    print(f"{Color.Bright.Blue}::{Color.White} Runing PostPilot {VERSION}"+Color.Reset)
    print(f"{Color.Bright.Blue}::{Color.White} Listening on {host}:{port}"+Color.Reset)
    
    app.run(host, port, debug=True, threaded=True)