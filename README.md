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

## running code

If JAVA_HOME is not initialized (VA Azure Virtual Desktop), place a file .javarc in your home directory.
It should contain the path for JAVA_HOME, where Java JDK 21+ is installed:
```
JAVA_HOME=R:/path/jdk21
```

## package publishing instructions

```
python -m build
twine upload dist/*
```