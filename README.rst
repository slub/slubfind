========
slubfind
========

With ``slubfind`` you can query data exports from the `SLUB catalogue <https://katalog.slub-dresden.de>`_
in Python.

This package is based on `txpyfind <https://github.com/slub/txpyfind>`_,
which enables access to data exports from `TYPO3-find <https://github.com/subugoe/typo3-find>`_.

Installation
============

... via PyPI
~~~~~~~~~~~~

.. code-block:: bash

   pip install slubfind

... or from Github source
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install git+https://github.com/slub/slubfind.git


Usage Example
=============

.. code-block:: python

   from slubfind.client import SlubFind
   # create SlubFind instance
   slub_find = SlubFind()
   # retrieve JSON data (query view, app format)
   slub_q = slub_find.app_search("manfred bonitz")
   # retrieve JSON data (detail view, app format)
   slub_doc = slub_find.app_document("0-1132486122")
