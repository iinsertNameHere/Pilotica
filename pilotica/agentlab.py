import os
import requests
import subprocess
from .console import Logger, Color
from tqdm import tqdm
from uuid import uuid4 as uuid
import tarfile
import zipfile
import json
import re

logger = Logger()

from urllib import request

def internet_on():
    try:
        request.urlopen('https://google.com', timeout=1)
        return True
    except: 
        return False

def downoad_latest_go():
    if not internet_on():
        logger.error("No internet connection!\n   Skiping go update...")
        return

    logger.info("Updating to latest go version...")

    go_version = requests.get("https://go.dev/VERSION?m=text").text.split("\n")[0]

    from .settings import instance_path
    versionfile = os.path.join(instance_path, 'GOVERSION.txt')

    if os.path.exists(versionfile):
        with open(versionfile, 'r') as file:
            version = file.read()
        if version == go_version:
            logger.info("Go version is up to date!")
            return

    # Download the Go release file
    if os.name == 'nt':
        response = requests.get(f"https://golang.org/dl/{go_version}.windows-amd64.zip", stream=True)
    else:
        url = f"https://golang.org/dl/{go_version}.linux-amd64.tar.gz"
        response = requests.get(url, stream=True)
    file_size = int(response.headers.get("Content-Length", 0))
    file_path = os.path.join(instance_path, f"latest-go.{'zip' if os.name == 'nt' else 'tar.gz'}")

    with open(file_path, "wb") as file:
        with tqdm(
            desc="Downloading Go",
            total=file_size,
            ascii=" ▖▘▝▗▚▞█",
            unit_scale=True,
            unit_divisor=1024,
            bar_format="{desc}: |{bar}| {n_fmt}B/{total_fmt}B {percentage:.2f}%",
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

    logger.success(f"{go_version} downloaded successfully")

    logger.info('Extracting go archive...')
    print(f"Golang Zip Path: {file_path}")
    
    try:
        if os.name != 'nt':
            with tarfile.open(file_path) as file:
                file.extractall(instance_path)
        else:
            with zipfile.ZipFile(file_path, 'r') as file:
                file.extractall(instance_path)
        logger.success("Extraction Finished!")
        with open(versionfile, 'w') as file:
            file.write(go_version)
    except:
        logger.error("Extraction Failed!")

def download_obfuscator():
    if not internet_on():
        logger.error("No internet connection!\n   Skiping garble update...")
        return

    logger.info("Updating to latest garble version...")

    latest = json.loads(requests.get("https://api.github.com/repos/burrowers/garble/releases/latest").text)["tag_name"]

    from .settings import instance_path
    go_path = os.path.join(instance_path, 'go', 'bin', 'go' + ('exe' if os.name == 'nt' else ''))

    os.environ['GOBIN'] = os.path.join(instance_path, 'go', 'bin')

    garble_path = os.path.join(instance_path, 'go', 'bin', 'garble')
    try:
        output = subprocess.check_output([garble_path, 'version']).decode('utf-8')
        version_number = output.strip().split()[1]
    except:
        version_number = "0.0.0"

    if version_number != latest:
        try:
            os.remove(garble_path)
        except:
            pass
        logger.info("Updating garble...")
        subprocess.run([go_path, "install", "mvdan.cc/garble@latest"])
        logger.success("Finished Uptade!")
    else:
        logger.info("Garble version is up to date!")

def get_values(go_src) -> dict:
    with open(go_src, 'r') as file:
        content = file.read()
    pattern = r'@(\w+)@'

    matches = re.findall(pattern, content)
    ret = dict()
    for key in matches:
        if key == "UUID" or key == "uuid":
            ret[key] = str(uuid())
        else:
            ret[key] = str()
    
    return ret

def pre_compile_go(go_src, values):
    with open(go_src, 'r') as file:
        conent = file.read()
    precomp = conent
    for key in values.keys():
        logger.custom("defined "+Color.Bright.Blue+"@"+key+"@ "+Color.Bright.Yellow+values[key], Color.Bright.Magenta, False, "::")
        precomp = precomp.replace("@"+key+"@", values[key])
    
    with open(go_src, "w") as file:
        file.write(precomp)
    
def compile_go(go_src: str, output_binary: str, obfuscate=False, target_os='windows', pre_values=None) -> bool:
    compiler = 'go'
    if obfuscate:
        compiler = 'garble'

    logger.custom("Compiling using "+compiler, Color.Bright.Magenta, True, "🛠️", end=f" 🛠️{Color.Reset}\n")

    if os.name == 'nt':
        compiler += '.exe'

    origin = ""
    if pre_values != None:
        with open(go_src, "r") as f:
            origin = f.read()

        pre_compile_go(go_src, pre_values)

    from .settings import instance_path

    command = [os.path.join(instance_path, "go", "bin", compiler), "build", '-o', output_binary]
    print(command)
    if target_os == 'windows-dll':
        target_os = "windows"
        os.environ["CGO_ENABLED"] = str(1)
        command.append("-buildmode=c-shared")
    command.append(go_src)

    os.environ['GOOS'] = target_os

    def reset():
        if pre_values != None:
            with open(go_src, "w") as f:
                f.write(origin)

    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError:
        reset()
        logger.custom("Failed to Compiled '"+go_src+"' to '"+output_binary+"'", Color.Bright.Red, False, "::")
        return False

    reset()

    logger.custom("Compiled '"+go_src+"' to '"+output_binary+"'", Color.Bright.Green, False, "::")
    return True