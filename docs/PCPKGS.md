📦 PCPKGS
======

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
>   - **`Items`** *(`string`)* *Scope name*

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