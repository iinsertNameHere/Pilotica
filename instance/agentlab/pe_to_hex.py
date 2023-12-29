import sys

def format_dll_for_go(dll_path, var_name="hostingDLL"):
    with open(dll_path, 'rb') as file:
        data = file.read()
        hex_data = data.hex()

        # Format the hex data for Go
        formatted_data = "0x" + hex_data

        print(f"var {var_name} = []byte{{ {formatted_data} }}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_dll>")
        sys.exit(1)

    dll_path = sys.argv[1]
    format_dll_for_go(dll_path)

if __name__ == "__main__":
    main()
