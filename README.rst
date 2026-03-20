========
slubfind
========

With ``slubfind`` you can query data exports from the `SLUB catalog <https://katalog.slub-dresden.de>`_
in Python.

This package is based on `txpyfind <https://github.com/slub/txpyfind>`_,
which enables access to data exports from `TYPO3-find <https://github.com/subugoe/typo3-find>`_.

Installation
============

... via PyPI
~~~~~~~~~~~~

.. code-block:: bash

   pip install slubfind

... or from GitHub source
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install git+https://github.com/slub/slubfind.git


Command-Line Usage
==================

After installation, the ``slubfind`` command is available (also via ``python -m slubfind``).
The base URL defaults to ``https://katalog.slub-dresden.de``.

Query
~~~~~

Execute a search query in app format:

.. code-block:: bash

   slubfind query "manfred bonitz"

With a facet filter and pagination:

.. code-block:: bash

   slubfind query "python" --facet "format_de14=Book, E-Book" --page 1 --count 10

Document
~~~~~~~~

Fetch a single document by ID in app format:

.. code-block:: bash

   slubfind document "0-1132486122"

Scroll
~~~~~~

Fetch all results for a query:

.. code-block:: bash

   slubfind scroll "manfred bonitz" --batch 10

Stream results as JSONL (one JSON object per line), useful for piping:

.. code-block:: bash

   slubfind scroll "manfred bonitz" --stream | jq .id

Settings
~~~~~~~~

Show TYPO3-find settings:

.. code-block:: bash

   slubfind settings

Solr Parameters
~~~~~~~~~~~~~~~

Show Solr parameters for a query:

.. code-block:: bash

   slubfind solr-params "manfred bonitz"

Solr Request
~~~~~~~~~~~~

Show Solr request URL for a query:

.. code-block:: bash

   slubfind solr-request "manfred bonitz"

Show Request URL
~~~~~~~~~~~~~~~~

Use ``--show-url`` to print the request URL instead of fetching the response.
This works with all subcommands:

.. code-block:: bash

   slubfind --show-url query "python" --facet "format_de14=Book, E-Book"
   slubfind --show-url document "0-1132486122"
   slubfind --show-url scroll "python" --batch 10

Export Format
~~~~~~~~~~~~~

Use ``--export-format`` to select the output format. The default is ``app``.

Fetch a document in JSON-LD format:

.. code-block:: bash

   slubfind document "0-1132486122" --export-format json-ld

Search in JSON-LD format:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format json-ld

Environment Variable
~~~~~~~~~~~~~~~~~~~~

Set ``SLUBFIND_URL`` to override the default base URL:

.. code-block:: bash

   export SLUBFIND_URL=https://katalog.slub-dresden.de
   slubfind query "manfred bonitz"

Python Usage Example
====================

.. code-block:: python

   from slubfind.client import SlubFind
   # create SlubFind instance
   slub_find = SlubFind()
   # retrieve JSON data (query view, app format)
   slub_q = slub_find.app_search("manfred bonitz")
   # retrieve JSON data (detail view, app format)
   slub_doc = slub_find.app_document("0-1132486122")
   # retrieve JSON-LD data (detail view)
   slub_jsonld = slub_find.jsonld_document("0-1132486122")
   # retrieve JSON-LD data (query view)
   slub_jsonld_q = slub_find.jsonld_search("manfred bonitz")
