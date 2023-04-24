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
        self.log_prefix = prefix
        self.active = active

        self.colors = {
            "warning": Color.Yellow,
            "error": Color.Red,
            "success": Color.Green,
            "info": Color.Bright.Blue,
        }
    
    def _log(self, type: str, msg: str, prefix: str = str(), full_color: bool = False):
        print(
            prefix, self.colors[type],
            f"{self.log_prefix}{'' if full_color else Color.White} {msg}",
            sep="",
            end=f"{Color.Reset}\n")

    def warning(self, msg, prefix: str = str(), full_color: bool = False):
        if self.active:
            self._log("warning", msg, prefix=prefix, full_color=full_color)

    def error(self, msg, prefix: str = str(), full_color: bool = False):
        if self.active:
            self._log("error", msg, prefix=prefix, full_color=full_color)

    def success(self, msg, prefix: str = str(), full_color: bool = False):
        if self.active:
            self._log("success", msg, prefix=prefix, full_color=full_color)

    def info(self, msg, prefix: str = str(), full_color: bool = False):
        if self.active:
            self._log("info", msg, prefix=prefix, full_color=full_color)