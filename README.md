
<h1 align="center">
  <br>
  <img src="static/logo.svg" width=400>
  <br>
</h1>

<h4 align="center">A post exploitation framework build on <a href="https://flask.palletsprojects.com">Flask</a>.</h4>
<h4 align="center">Developed for the sake of learning about post exploitation!!!</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-green?style=flat" alt="Python" />
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"></a>
</p>

<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-terminology">Terminology</a> •
  <a href="#-how-to-use">How To Use</a> •
  <a href="#-pcpkgs">PCPKGS</a> •
  <a href="#-service-api">Service-API</a> •
  <a href="#-license">License</a>
</p>

<p align="center">
    <img src="static/screenshot.png" width="500">
</p>

## 📊 Key Features

* The ability to write own clients and agents using the <a href="#service-api">Service-API</a>
* A Plugin System (<a href="#pcpkgs">Pilotica-Component-Packages</a>)
* Build in Webinterface and Agent builder
* Cross platform
  - Windows and Linux

## 🔥 Installation

The installation process is very easy!
Just clone the repository, generate all requirements and run Pilotica!

```bash
# Using git to clone the repo
$ git clone https://github.com/iinsertNameHere/Pilotica.git

# Go into the repository folder
$ cd Pilotica

# Install all Python requirements
$ pip install -r requirements.txt

# Generate all required Component-Packages
$ python3 pcpkger.py --auto

# Run Pilotica
$ python3 pilotica.py
```

> **Note**
> If you're using Windows, you could also download the repo as a zip file.

## 💬 Terminology
**Operator:**<br>
Refers to the user of the Pilotica framework who utilizes its features and functionalities to operate and manage their systems.

**Agent:**<br>
Refers to the payload that is deployed on target systems to facilitate communication between the Operators and the target systems.

**pcpkg:**<br>
Refers to the Pilotica-Component-Package, which is a plugin or add-on that extends the capabilities of the framework. These packages are pre-built and can be easily integrated into the framework.

**Service-API:**<br>
Refers to the C2 Server API, which is responsible for handling the communication between the Operator and the target systems. This API allows the Operator to execute various commands and receive data from the target systems.*

## 🗃️ How To Use

* The simplest way to use Pilotica is to just run the file from the terminal without any arguments and without touching the config file:
    - This will run run Pilotica With logging enabled by default.

* The config file can be found in /instance/config and is named `config.yaml`.

>## Config Schema
>
>### **Properties:**
>
>- **`pilotica`** *(`object`)*
>  - **`DEBUG`** *(`boolean`)* *Sets debug mode for pilotica*
>  - **`API_LOGGING`** *(`boolean`)* *Enables Service-API logging*
>  - **`secret_key`** *(`string`)* *Sets Service-API key*
>    - If set to `RANDOM` generates new key every session.
>- **`components`** *(`array`)* *(not required)* *A list of all pcpkgs to load*
>  - **`Items`** *(`object`)*
>    - **`alias`** *(`string`)* *Alias of the package*
>    - **`logging`** *(`boolean`)* *Enables logging for the package*
>
> If components is not set, Pilotica will display a warning at
> startup because this is not recommended!

## 📦 PCPKGS
[Pilotica-Component-Package documentation](docs/PCPKGS.md)

## 🖥️ Service API
[Service-API documentation](docs/SERVICEAPI.md)

### License

>This Project is Licensed under the terms of [Apache-2.0 license](LICENCE)!
