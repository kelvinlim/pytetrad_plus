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

If JAVA_HOME is not initialized (VA Azure Virtual Desktop), place a file .javarc in your home directory. This is generally not needed
for linux or macos.
It should contain the path for JAVA_HOME, where Java JDK 21+ is installed.

Other paths include those for graphviz and for other executables

```
JAVA_HOME="C:/Users/VHAMINLimK/OneDrive - Department of Veterans Affairs/CDA/jdk21.0.4_7"
GRAPHVIZ_BIN="C:/Users/VHAMINLimK/OneDrive - Department of Veterans Affairs/CDA/windows_10_msbuild_Release_graphviz-9.0.0-win32/Graphviz/bin"
BIN="C:/Users/VHAMINLimK/OneDrive - Department of Veterans Affairs/CDA/bin"

```
To run the test program:
```
./pytetrad_plus/mypytetrad.py
```

This should do the search and place the results in ./pytetrad_plus/boston_result.json.

## package publishing instructions

```
python -m build
twine upload dist/*
```