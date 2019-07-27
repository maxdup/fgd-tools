Quickstart
==========

Get yourself up in running quickly.

Installation
------------

PyPI
~~~~
Fgd-tools is available on the Python Package Index. This makes installing it with pip as easy as:

.. code-block:: bash

   pip3 install fgdtools

Git
~~~

If you want the latest code or even feel like contributing, the code is available on GitHub.

You can easily clone the code with git:

.. code-block:: bash

   git clone git://github.com/maxdup/fgd-tools.git

and install it with:

.. code-block:: bash

   python3 setup.py install

Usage
-----

Here's a few example usage of fgd-tools

Parsing
~~~~~~~

You can get a Fgd object by parsing an .fgd file using FgdParse

.. code-block:: python

   > from fgdtools import FgdParse

   > fgd = FgdParse('C:/Program Files (x86)/Steam/steamapps/common/Team Fortress 2/bin/tf.fgd')

Writing
~~~~~~~

You can write an .fgd file from a Fgd object.

.. note::
   Parsing/writing is destructive. Comments will be ignored. Include statements will be removed and have everything merged in the same fgd. The original structure of the file may be modified. The actual data about entities and the inheritance hierarchy is untouched however.

.. code-block:: python

   > from fgdtools import FgdWrite

   > FgdWrite(fgd, 'tf-clone.fgd')

Getting entity schemas
~~~~~~~~~~~~~~~~~~~~~~

You can get entity schematics from an Fgd object.

.. code-block:: python

   > env_fire = fgd.entity_by_name('env_fire')
   > print(env_fire.schema)

   {'properties': {'targetname': {'type': 'string', 'description': 'The name...'}, ...},
   'inputs': {'StartFire': {'type': 'void', 'description': 'Start the fire'}, ...},
   'outputs': {'onIgnited': {'type': 'void', 'description':'Fires when...'}, ...}}

Terminology
-----------
Here are some color coded charts for the terminology used in this library for fgd files.

FgdEntity
~~~~~~~~~
.. image:: /_static/fgdentity.jpg

FgdEntityProperty
~~~~~~~~~~~~~~~~~
.. image:: /_static/fgdentityproperty.jpg

FgdEntityPropertyOption
~~~~~~~~~~~~~~~~~~~~~~~
.. image:: /_static/fgdentitypropertyoption.jpg

FgdEntityInput/Output
~~~~~~~~~~~~~~~~~~~~~
.. image:: /_static/fgdentityio.jpg
