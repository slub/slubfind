========
slubfind
========

``slubfind`` is a command-line tool and Python library for querying the
`library catalog <https://katalog.slub-dresden.de>`_ of SLUB Dresden
(Saxon State Library – Dresden State and University Library). It retrieves
catalog records in multiple formats including SLUBApp data, JSON-LD linked
data, Solr responses, and holding/availability information.

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

``--page`` and ``--count`` must be non-negative integers (``>= 0``).

Exclude facet data from query output:

.. code-block:: bash

   slubfind query "manfred bonitz" --no-facets

Document
~~~~~~~~

Fetch a single document by ID:

.. code-block:: bash

   slubfind document 0-1132486122

Return a non-zero exit code when a document is not found:

.. code-block:: bash

   slubfind document 0-DOES-NOT-EXIST --strict-not-found

Return no output (without failing) when a document is not found:

.. code-block:: bash

   slubfind document 0-DOES-NOT-EXIST --lazy-not-found

Scroll
~~~~~~

Fetch all results for a query:

.. code-block:: bash

   slubfind scroll "manfred bonitz" --batch 10

``--batch`` must be a positive integer (``> 0``).

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

.. code-block:: bash

   slubfind solr-params --from-url "https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz"

Show Request URL
~~~~~~~~~~~~~~~~

Use ``--show-url`` to print the request URL instead of fetching the response.
This works with ``query``, ``document``, and ``scroll``:

.. code-block:: bash

   slubfind --show-url document 0-1132486122

.. code-block:: bash

   slubfind --show-url query "manfred bonitz" --facet "format_de14=Book, E-Book"

.. code-block:: bash

   slubfind --show-url scroll "manfred bonitz" --batch 10

Export Format
~~~~~~~~~~~~~

Use ``--export-format`` to select the output format. The default is ``app``.

Available formats and their supported subcommands:

- ``app`` (default) - SLUBApp data (``query``, ``document``)
- ``json-ld`` - JSON-LD linked data (``query``, ``document``)
- ``json-solr-results`` - Solr results (``query`` only)
- ``raw-solr-response`` - raw Solr response (``query`` only)
- ``json-holding-status`` - access links, supplementary information, and references (``document`` only)
- ``json-holding-status-index`` - availability status, shelf location, and links (``document`` only)

The ``scroll`` subcommand always uses ``raw-solr-response`` internally.
The formats ``json-all``, ``json-solr-params``, and ``json-solr-request`` are used
internally by the ``settings``, ``solr-params``, and ``solr-request`` subcommands.

Fetch a document in JSON-LD format:

.. code-block:: bash

   slubfind document 0-1132486122 --export-format json-ld

Search in JSON-LD format:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format json-ld

Fetch access links and references for a document:

.. code-block:: bash

   slubfind document 0-320589099 --export-format json-holding-status

Fetch availability status and location for a document:

.. code-block:: bash

   slubfind document 0-1809383722 --export-format json-holding-status-index

Query with Solr results format:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format json-solr-results

Query with raw Solr response:

.. code-block:: bash

   slubfind query "manfred bonitz" --export-format raw-solr-response

Raw Server Output
~~~~~~~~~~~~~~~~~

Use ``--no-parser`` to skip response parsing and print the raw server output.
This is useful for inspecting the exact response or piping to other tools:

.. code-block:: bash

   slubfind query "manfred bonitz" --no-parser

.. code-block:: bash

   slubfind document 0-1132486122 --no-parser --export-format json-holding-status

Environment Variable
~~~~~~~~~~~~~~~~~~~~

Set ``SLUBFIND_URL`` to override the default base URL:

.. code-block:: bash

   export SLUBFIND_URL=https://katalog.slub-dresden.de

.. code-block:: bash

   slubfind query "manfred bonitz"

Testing
=======

Run default tests (offline/unit):

.. code-block:: bash

   pytest

Run integration tests against the live catalog:

.. code-block:: bash

   pytest --override-ini addopts="" -m integration

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
   # retrieve access links, references (detail view)
   slub_hs = slub_find.holding_status_document("0-1132486122")
   # retrieve availability status and location (detail view)
   slub_hsi = slub_find.holding_status_index_document("0-1132486122")
   # retrieve raw Solr response
   slub_raw = slub_find.raw_solr_search("manfred bonitz")
   # retrieve Solr result documents only
   slub_solr = slub_find.solr_results_search("manfred bonitz")
   # retrieve Solr parameters for a query
   slub_params = slub_find.solr_params("manfred bonitz")
   # retrieve Solr request URL for a query
   slub_req = slub_find.solr_request("manfred bonitz")
   # retrieve TYPO3-find settings
   slub_settings = slub_find.settings()
