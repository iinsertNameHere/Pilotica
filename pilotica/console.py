class _bright:
    Red     : str = "\u001b[31;1m"
    Green   : str = "\u001b[32;1m"
    Yellow  : str = "\u001b[33;1m"
    Blue    : str = "\u001b[34;1m"
    Magenta : str = "\u001b[35;1m"
    Cyan    : str = "\u001b[36;1m"
    White   : str = "\u001b[37;1m"

class _color:   
    Black          : str = "\u001b[30m"
    Red            : str = "\u001b[31m"
    Green          : str = "\u001b[32m"
    Yellow         : str = "\u001b[33m"
    Blue           : str = "\u001b[34m"
    Magenta        : str = "\u001b[35m"
    Cyan           : str = "\u001b[36m"
    White          : str = "\u001b[37m"
    Reset          : str = "\u001b[0m"
    Bright = _bright()

Color = _color()

class Logger:
    def __init__(self, prefix: str = '::', active: bool = True):
        self._log_prefix = prefix
        self._active = active

        self._colors = {
            "warning": Color.Yellow,
            "error": Color.Red,
            "success": Color.Green,
            "info": Color.Bright.Blue,
        }
    
    def _log(self, type: str, msg: str, prefix: str = str(), full_color: bool = False):
        if self._active:
            print(f"{prefix}{self._colors[type]}{self._log_prefix}{'' if full_color else Color.White} {msg}",
                end=f"{Color.Reset}\n")

    def warning(self, msg: str, prefix: str = str(), full_color: bool = False):
        self._log("warning", msg, prefix=prefix, full_color=full_color)

    def error(self, msg: str, prefix: str = str(), full_color: bool = False):
        self._log("error", msg, prefix=prefix, full_color=full_color)

    def success(self, msg: str, prefix: str = str(), full_color: bool = False):
        self._log("success", msg, prefix=prefix, full_color=full_color)

    def info(self, msg: str, prefix: str = str(), full_color: bool = False):
        self._log("info", msg, prefix=prefix, full_color=full_color)

    def custom(
        self,
        msg: str,
        color: str,
        full_color: bool,
        log_prefix: str,
        end=f"{Color.Reset}\n"
    ):
        if self._active:
            print(f"{color}{log_prefix}{'' if full_color else Color.White} {msg}", end=end)

    def prompt_YesNo(self, prompt: str, color: str) -> bool:
        yes_choices = ['yes', 'y']
        no_choices = ['no', 'n']

        error_color = self._colors['error']

        while True:
            choice = input(f"{color}{self._log_prefix} {Color.Bright.Green}[Y]es [N]o{Color.White} {prompt} ")
            if choice in yes_choices:
                return True
            elif choice in no_choices:
                return False
            else:
                self._log("error", f"Invalid prompt answere, only {error_color}'yes' ('y'){Color.White} or {error_color}'no' ('n'){Color.White} are allowed!")