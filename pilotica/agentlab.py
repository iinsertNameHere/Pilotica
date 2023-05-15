import os
import requests
import subprocess
from .console import Logger
from .settings import instance_path
from tqdm import tqdm
import tarfile
import zipfile

logger = Logger()

def parse_filesize(bytes, units=
[
    (1<<50, ' PB'),
    (1<<40, ' TB'),
    (1<<30, ' GB'),
    (1<<20, ' MB'),
    (1<<10, ' KB'),
    (1, (' byte', ' bytes')),
]):
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return amount, suffix

def downoad_latest_go():
    go_version = requests.get("https://go.dev/VERSION?m=text").text

    versionfile = os.path.join(instance_path, 'GOVERSION.txt')

    if os.path.exists(versionfile):
        with open(versionfile, 'r') as file:
            version = file.read()
        if version == go_version:
            logger.info("Go version is up to date!")
            return
    # Get the download URL for the latest Go release
    url = f"https://golang.org/dl/{go_version}.{'windows-amd64.zip' if os.name == 'nt' else 'linux-amd64.tar.gz'}"

    # Download the Go release file
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
    go_path = os.path.join(instance_path, 'go', 'bin', 'go' + ('exe' if os.name == 'nt' else ''))

    os.environ['GOBIN'] = os.path.join(instance_path, 'go', 'bin')

    logger.info("Updating garble...")
    subprocess.run([go_path, "install", "mvdan.cc/garble@latest"])
    logger.success("Finished Uptade!")


def compile(go_src_directory, output_binary_path, obfuscate=False, target_os='windows'):
    compiler = 'go'
    if obfuscate:
        compiler = 'garble'

    if os.name == 'nt':
        compiler += '.exe'

    os.environ['GOOS'] = target_os

    subprocess.run([os.path.join(instance_path, "go", "bin", compiler), "build", '-o', output_binary, src_directory])


# Example usage
src_directory = "./test/main.go"
output_binary = "./test/out.bin"

instance_path = os.path.abspath('./instance')

downoad_latest_go()
download_obfuscator()

compile(src_directory, target_os='linux')