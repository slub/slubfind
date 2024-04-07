========
slubfind
========

``slubfind`` allows to query data exports from the SLUB catalogue. It is based on the
Python package `txpyfind <https://github.com/herreio/txpyfind>`_ which enables access
to data exports from TYPO3-find in Python.

Installation
============

... via SSH
~~~~~~~~~~~

.. code-block:: bash

   pip install -e git+ssh://git@github.com/herreio/slubfind.git#egg=slubfind

... or via HTTPS
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e git+https://github.com/herreio/slubfind.git#egg=slubfind


Usage Example
=============

.. code-block:: python

   import slubfind
