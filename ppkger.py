from pilotica.plugin.generation import PluginCompiler
import sys
import os

def usage(exit_code: int):
    print(f"Usage: {os.path.basename(__file__)} [-h|--help] srcFolder dstFolder\n")
    exit(exit_code)

if __name__ == "__main__":
    print_usage = False
    try:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print_usage = True
        else:
            src_folder = sys.argv[1]
            dst_folder = sys.argv[2]
    except:
        usage(-1)

    if print_usage:
        usage(0)

    pluginCompiler = PluginCompiler()

    pluginCompiler.validate(src_folder)
    pluginCompiler.compile(src_folder, dst_folder)