To use this program, the Visual Studio 2010  Ultimate has to be installed previously.

use 
`conda env export -n env_name > environment.yaml` and `pip freeze > requirements.txt` to export the environment of the conda and pip.


use `conda env create -n env_name -f environment.yaml` and `pip install -r requirement.txt` to create the same environment on the new setup. 

The environment need the support of the following python package:
- numpy