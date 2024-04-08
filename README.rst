========
slubfind
========

With ``slubfind`` you can query data exports from the SLUB catalogue in Python.

This package is based on `txpyfind <https://github.com/herreio/txpyfind>`_,
which enables access to data exports from TYPO3-find.

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

   from slubfind.client import SlubFind
   # create SlubFind instance
   slub_find = SlubFind()
   # retrieve JSON data (query view, app format)
   slub_q = slub_find.app_search("manfred bonitz", count=32)
   # retrieve JSON data (detail view, app format)
   slub_doc = slub_find.app_details("0-1132486122")
