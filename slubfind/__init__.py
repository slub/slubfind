"""
With ``slubfind`` you can query data exports from the SLUB catalog.
"""
from . import client, parser
from ._version import __version__, version, version_tuple

__all__ = ["client", "parser", "__version__", "version", "version_tuple"]
