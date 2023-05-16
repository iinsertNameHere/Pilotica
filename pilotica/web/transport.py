from ..components.decorators import *

@EnableComponents(globals(), "transport", args=["data", "direction"])
def Transport(data, direction="in"): # in out
    HANDLE_PCPKGS
    retlen = len(component_returns)
    if retlen > 0:
        data = component_returns[retlen-1]
    return data