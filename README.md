
<h1 align="center">
  <br>
  <img src="static/logo.svg" width=400>
  <br>
</h1>

<h4 align="center">A post exploitation framework build on <a href="https://flask.palletsprojects.com">Flask</a>.</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-green?style=flat" alt="Python" />
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"></a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#pcpkgs">PCPKGS</a> •
  <a href="#license">License</a>
</p>

<p align="center">
    <img src="static/screenshot.png" width="500">
</p>

## Key Features

* The ability to write own clients and agents using the <a href="#service-api">Service-API</a>
* A Plugin System (<a href="#pcpkgs">Pilotica-Component-Packages</a>)
* Build in Webinterface
* Cross platform
  - Windows, macOS and Linux ready.

## Installation

The installation process is very easy!
Just clone the repository, generate all requirements and run Pilotica!

```bash
# Using git to clone the repo
$ git clone https://github.com/iinsertNameHere/Pilotica.git

# Go into the repository folder
$ cd Pilotica-main

# Install all Python requirements
$ pip install -r requirements.txt

# Generate all required Component-Packages
$ python3 pcpkger.py --auto

# Run Pilotica
$ python3 pilotica.py
```

> **Note**
> If you're using Windows, you could also download the repo as a zip file.

## How To Use

* The simplest way to use Pilotica is to just run the file from the terminal without any arguments and without touching the config file:
    - This will run run Pilotica With logging enabled and with the Component-Package "transport-base64" loaded, with will encode all data that is transported using base64.

* The config file can be found in /instance/config and is named "config.yaml" by default.

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
>  - **Items** *(`object`)*
>    - **`alias`** *(`string`)* *Alias of the package*
>    - **`logging`** *(`boolean`)* *Enables logging for the package*
>
> If components is not set, Pilotica will display a warning at
> startup because this is not recommended!

## PCPKGS
PCPKGS (Pilotica-Component-Packages) are basicly zip files that contain 2 main files:
* A Python bytecode file: base.pyc
* A metadata file: meta.yaml

.pcpkg files are build from a source directory using the pcpkger (Pilotica-Component Packager) tool.

The basic source directory tree should look like this to be valid:
```bash
src-dir
   ├── meta.yaml # Metadata file
   └── base.py # Main-Script file
```

### **The Metadata file**:
>## Metadata Schema
>
>### **Properties:**
>
>- **`name`** *(`string`)* *The full name of the package*
>- **`alias`** *(`string`)* *The alias that the package is referred by*
>- **`creator`** *(`string`)* *The name of the creator of the package*
>- **`version`** *(`string`)* *The package version*
>- **`description`** *(`string`)* *What dose the package do?*
>- **`scopes`** *(`array`)* *All the scopes that the package wants to access*
>  - **Items** *(`string`)* *A scope name*

This is the Schema a meta.yaml file has to follow.

### **The Main-Script file**:

>## Main-Scrip Rules
>
> * Needs to have a class called *`Scopes`*
>   - This class should contain functions with the name of the scope they want to access. These function must take two arguments: `self` and `**kwargs`
>   - This class should have a decorator called **`@Scropes`** that must be imported from the components code api lib *"`pilotica.components.api`"*
>
> * Scopes:
>   - core
>     - The *core* scope will be executed right before the flask server is started. 
>     - Has to return `None`, `True` or `False`
>   - transport
>     - The *transport* scope will be executed every time a data is comming in or is going out of the server.
>      - It gets passed down the transport `data` with must also be returnd and can be manipulated in the scope function.
>      - You can get the `data` from the `kwargs` argument like this: "`kwargs['data']`"
>      - If you don't want to use the data, just end the function like this "`return kwargs['data']`"
>   - service
>     - The *service* scope will be executed right when the Service-API is initialized.
>     - It gets passed down the current service modul as an object.
>     - You can get the `service_dict` (service module) from the `kwargs` argument like this: "`kwargs['service_dict']`"
>     - Has to return `None`, `True` or `False`

This are all the rules for the base.py file.

## License

>This Project is Licensed under the terms of [Apache-2.0 license](LICENCE)!