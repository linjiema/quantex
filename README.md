#Environment Settings
To use this program, the __Visual Studio 2010 Runtime__ has to be installed previously.

Use `conda env create -n quantex-py311 -f .\config\env_config.yaml` to create environment

use 
`conda env export -n quantex-py311 > .\config\env_config.yaml` and `pip freeze > requirements.yaml` to export the environment of the conda and pip.

use `conda env create -n quantex-py311 -f env_config.yaml` and `pip install -r requirement.txt` to create the same environment on the new setup. 

Use `conda env update -f .\config\env_config.yaml` to update the existed environment


---
## Environment Setup Instruction

1. Install ___Visual Studio 2010 C#___
2. Use `conda env create -n quantex-py311 -f .\Cache\Environment` create virtual environment 
3. Config __nv_experiment__ as Python Interpreter