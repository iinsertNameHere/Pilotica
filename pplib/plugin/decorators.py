import inspect
import types
import functools

def EnableMixins(_globals: dict, mixin_name: str, args: list = list(), returns: str = "plugin_returns"):
    """
    Use this Decorator to enable Mixin Handling for a function.

    *mixin_name* The name of the mixin function to execute

    *args* A list of variable names that will be forwarding to the Mixin function

    *returns* The name of the list that holds all plugin returns

    You can define where in the function the mixins are handled by placing the line HANDLE_MIXINS there.
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
     
        mixin_code = f'{returns}: list = list()\n' + \
                     f'for index in plugin_manager.get("{mixin_name}"):\n' + \
                     f'    {returns}.append(plugin_manager.plugins["all"][index].mixins.{mixin_name}({",".join(kwargs)}))'

        position = 1
        for i, line in enumerate(func_src[1:]):
            if line.strip() == "HANDLE_MIXINS":
                position = i+1
                break

        func_src.pop(position)

        mixin_code_lines = ["    "+line for line in mixin_code.split('\n')]
        if position <= len(func_src)-1:
            mixin_code_lines.reverse()
            for line in mixin_code_lines:
                func_src.insert(position, line)
        else:
            raise ValueError("position index out of range!")

        code = compile('\n'.join(func_src), "mixins_"+func.__name__, "exec")

        exec_globals = _globals
        exec(code, exec_globals)

        new_func = types.FunctionType(exec_globals[func.__name__].__code__, _globals, func.__name__)
        functools.update_wrapper(new_func, func)

        return new_func
    return decorator