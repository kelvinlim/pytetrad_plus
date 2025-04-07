# pytetrad_plus

Helper code for the pytetrad package.

Required packages
1. jpype
2. pytetrad

To install packages:
```
# create virtual environment and activate the environment
python -mvenv .venv
source .venv/bin/activate # linux
.venv\Scripts\Activate.ps1 # windows

# use pip to install
pip install -r requirements.txt
```


## package instructions

```
python -m build
twine upload dist/*
```