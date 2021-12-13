#Environment Settings
To use this program, the __Visual Studio 2010 Runtime__ has to be installed previously.

Use `conda env create -n env -f .\Cache\Environment_Requirements\environment.yaml` to create environment

use 
`conda env export -n env_name > .\Cache\Environment_Requirements\environment.yaml` and `pip freeze > .\Cache\Environment_Requirements\environment.yaml` to export the environment of the conda and pip.

use `conda env create -n env_name -f environment.yaml` and `pip install -r requirement.txt` to create the same environment on the new setup. 


---
## Environment Setup Instruction

1. Install ___Visual Studio 2010 C#___
2. Use `conda env create -n env -f .\Cache\Environment` create virtual environment 
3. Config __nv_experiment__ as Python Interpreter