"""
parser module of ``slubfind``
"""
from txpyfind.parser import JSONResponse


class AppDetails(JSONResponse):  # pylint: disable=R0903
    """
    Parser for app-format detail view responses.

    Expected structure::

        {
            "record": {"format": ..., "title": ..., ...},
            "id": "0-1132486122",
            "oa": 0,
            "thumbnail": "...",
            "copies": [...],
            "parts": {...}
        }
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict) and "id" in self.raw
        self.found = self.ok and isinstance(
            self.raw["id"], str) and len(self.raw["id"].strip()) > 0


class AppSearch(JSONResponse):  # pylint: disable=R0903
    """
    Parser for app-format search view responses.

    Expected structure::

        {
            "numFound": 42,
            "start": 0,
            "docs": [...],
            "facets": {...}
        }
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict) and "docs" in self.raw
        self.num_found = self.raw.get("numFound", 0) if self.ok else 0
        self.start = self.raw.get("start", 0) if self.ok else 0
        self.docs = self.raw.get("docs", []) if self.ok else []


class JsonLdResponse(JSONResponse):  # pylint: disable=R0903
    """
    Parser for JSON-LD responses (detail and search views).

    Expected structure::

        {
            "@context": {"so": "http://schema.org/"},
            "@graph": [
                {
                    "@id": "https://katalog.slub-dresden.de/id/0-...",
                    "so:name": "...",
                    "so:author": "...",
                    "so:url": "...",
                    "@type": "so:Book"
                }
            ]
        }
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict) and "@context" in self.raw
        self.graph = self.raw.get("@graph", []) if self.ok else []
