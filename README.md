[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/maxdup/fgd-tools/blob/master/LICENSE.txt)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/fgdtools.svg)](https://pypi.python.org/pypi/fgdtools/)
[![PyPI version fury.io](https://badge.fury.io/py/fgdtools.svg)](https://pypi.python.org/pypi/fgdtools/)
[![alt text](https://github.com/maxdup/fgd-tools/blob/master/docs/source/coverage.svg "coverage")]()

# Fgd-tools

Fgd-tools is a Python library for parsing .fgd files for the Source Engine level editor Hammer. It provides entity schemas and other level editor configuration information.

Full documentation: https://maxdup.github.io/fgd-tools/

## Installation

### PyPI

Fgd-tools is available on the Python Package Index. This makes installing it with pip as easy as:

```bash
pip3 install fgdtools
```

### Git

If you want the latest code or even feel like contributing, the code is available on GitHub.

You can easily clone the code with git:

```bash
git clone git://github.com/maxdup/fgd-tools.git
```

and install it with:

```bash
python3 setup.py install
```

## Usage

Here's a few example usage of fgd-tools

### Parsing

You can get a Fgd object by parsing an .fgd file using FgdParse

```python
>>> from fgdtools import FgdParse
>>> fgd = FgdParse('C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2/bin/tf.fgd')
```

### Writing

You can write an .fgd file from a Fgd object.


> Parsing/writing is destructive. Comments will be lost. The original structure of the file may be altered. The actual data about entities and the inheritance hierarchy is untouched however.

```python
>>> from fgdtools import FgdWrite
>>> FgdWrite(fgd, 'tf-clone.fgd')
```

### Getting entity schemas

You can get entity schematics from an Fgd object.

```python
>>> env_fire = fgd.entity_by_name('env_fire')
>>> print(env_fire.schema)
{'properties': {'targetname': {'type': 'string', 'description': 'The name...'}, ...},
'inputs': {'StartFire': {'type': 'void', 'description': 'Start the fire'}, ...},
'outputs': {'onIgnited': {'type': 'void', 'description':'Fires when...'}, ...}}
```

## Terminology

Here are some color coded charts for the terminology used in this library for fgd files.

### FgdEntity
![alt text](https://github.com/maxdup/fgd-tools/raw/master/docs/source/_static/fgdentity.jpg "FgdEntity terminology")

### FgdEntityInput/Output
![alt text](https://github.com/maxdup/fgd-tools/raw/master/docs/source/_static/fgdentityio.jpg "FgdEntityInput/Output terminology")

### FgdEntityProperty
![alt text](https://github.com/maxdup/fgd-tools/raw/master/docs/source/_static/fgdentityproperty.jpg "FgdEntityProperty terminology")

### FgdEntityPropertyOption
![alt text](https://github.com/maxdup/fgd-tools/raw/master/docs/source/_static/fgdentitypropertyoption.jpg "FgdEntityPropertyOption terminology")

### FgdEntitySpawnflag
![alt text](https://github.com/maxdup/fgd-tools/raw/master/docs/source/_static/fgdentityspawnflags.jpg "FgdEntitySpawnflag terminology")

