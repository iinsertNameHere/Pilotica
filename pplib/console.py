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

