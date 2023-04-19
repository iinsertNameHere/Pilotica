import inspect
import types
import functools

def EnableComponents(_globals: dict, scope_name: str, args: list = list(), returns: str = "component_returns"):
    """
    Use this Decorator to enable Component-Package Handling for a function.

    *scope_name* The name of the scope function to execute

    *args* A list of variable names that will be forwarding to the Scope function

    *returns* The name of the list that holds all scope returns

    You can define where in the function the Components are handled by placing the line HANDLE_PCPKGS there.
    """
    def decorator(func):
        # get the function source code
        lines = [line for line in inspect.getsource(func).split('\n')[1:]]
        func_src = [lines.pop(0).strip()]
        for line in lines:
            if line.strip() != "":
                func_src.append(line)

        kwargs = list()
        for arg in args:
            kwargs.append(f"{arg}={arg}")
     
        scope_code = f'from pilotica.settings import component_manager\n' + \
                     f'{returns}: list = list()\n' + \
                     f'for index in component_manager.get_byScope("{scope_name}"):\n' + \
                     f'    {returns}.append(component_manager.components.get("all")[index].scopes.{scope_name}({",".join(kwargs)}))'

        position = 1
        for i, line in enumerate(func_src[1:]):
            if line.strip() == "HANDLE_PCPKGS":
                position = i+1
                break

        func_src.pop(position)

        scope_code_lines = ["    "+line for line in scope_code.split('\n')]
        if position <= len(func_src):
            scope_code_lines.reverse()
            for line in scope_code_lines:
                func_src.insert(position, line)
        else:
            raise ValueError("position index out of range!")

        code = compile('\n'.join(func_src), _globals["__file__"], "exec")

        exec_globals = _globals
        exec(code, exec_globals)

        new_func = types.FunctionType(exec_globals[func.__name__].__code__, _globals, func.__name__)
        functools.update_wrapper(new_func, func)

        return new_func
    return decorator