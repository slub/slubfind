========
slubfind
========

``slubfind`` is a command-line tool and Python library for querying the
`SLUB catalog <https://katalog.slub-dresden.de>`_ — the public catalog of
SLUB Dresden (Saxon State and University Library). It retrieves catalog records
in multiple formats including structured app data, JSON-LD linked data, Solr
responses, and holding/availability information.

Under the hood, ``slubfind`` builds on `txpyfind <https://github.com/slub/txpyfind>`_,
a generic client for `TYPO3-find <https://github.com/subugoe/typo3-find>`_ catalog
frontends.

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

Execute a search query:

.. code-block:: bash

   slubfind query "manfred bonitz"

With a facet filter and pagination:

.. code-block:: bash

   slubfind query "manfred bonitz" --facet "format_de14=Book, E-Book" --page 1 --count 10

Document
~~~~~~~~

Fetch a single document by ID:

.. code-block:: bash

   slubfind document 0-1132486122

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

From URL
~~~~~~~~

Use ``--from-url`` to query using a SLUB catalog URL instead of individual parameters.
This works with ``query``, ``scroll``, ``solr-params``, and ``solr-request``:

.. code-block:: bash

   slubfind query --from-url "https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz"
   slubfind solr-params --from-url "https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz"

Show Request URL
~~~~~~~~~~~~~~~~

Use ``--show-url`` to print the request URL instead of fetching the response.
This works with all subcommands:

.. code-block:: bash

   slubfind --show-url query "manfred bonitz" --facet "format_de14=Book, E-Book"
   slubfind --show-url document 0-1132486122
   slubfind --show-url scroll "manfred bonitz" --batch 10

Export Format
~~~~~~~~~~~~~

Use ``--export-format`` to select the output format. The default is ``app``.

Available formats and their supported subcommands:

- ``app`` (default) — structured app format (``query``, ``document``)
- ``json-ld`` — JSON-LD linked data (``query``, ``document``)
- ``json-holding-status`` — full-text access and reference links (``document`` only)
- ``json-holding-status-index`` — resource and related links (``document`` only)
- ``json-solr-results`` — Solr results (``query`` only)
- ``raw-solr-response`` — raw Solr response (``query`` only)

The ``scroll`` subcommand always uses ``raw-solr-response`` internally.
The formats ``json-all``, ``json-solr-params``, and ``json-solr-request`` are used
internally by the ``settings``, ``solr-params``, and ``solr-request`` subcommands.

Fetch a document in JSON-LD format:

.. code-block:: bash

   slubfind document 0-1132486122 --export-format json-ld

Search in JSON-LD format:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format json-ld

Fetch holding status for a document:

.. code-block:: bash

   slubfind document 0-320589099 --export-format json-holding-status

Fetch indexed holding status for a document:

.. code-block:: bash

   slubfind document 0-1809383722 --export-format json-holding-status-index

Query with Solr results format:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format json-solr-results

Query with raw Solr response:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format raw-solr-response

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
   # retrieve holding status (detail view)
   slub_hs = slub_find.holding_status_document("0-1132486122")
