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
        self.id = self._field("id")

    def _unescape_dict(self, d):
        """Apply inherited _unescape() to each value of a dict."""
        if not isinstance(d, dict):
            return d
        return {k: self._unescape(v) for k, v in d.items()}

    @property
    def record(self):
        """Return the unescaped record dict."""
        raw_record = self.raw.get("record") if self.ok else None
        if isinstance(raw_record, dict):
            return self._unescape_dict(raw_record)
        return None

    @property
    def title(self):
        """Return the title from the record dict."""
        rec = self.record
        return rec.get("title") if rec else None

    @property
    def format(self):
        """Return the format from the record dict."""
        rec = self.record
        return rec.get("format") if rec else None

    @property
    def contributor(self):
        """Return the contributor from the record dict."""
        rec = self.record
        return rec.get("contributor") if rec else None

    @property
    def identifier(self):
        """Return the identifier from the record dict."""
        rec = self.record
        return rec.get("identifier") if rec else None


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


class JsonLdDetails(JsonLdResponse):  # pylint: disable=R0903
    """Parser for JSON-LD detail view responses."""

    def __init__(self, plain):
        super().__init__(plain)
        self.found = self.ok and len(self.graph) > 0 and not (
            self.graph[0].get("@id", "").rstrip("/").endswith("/id"))

    @property
    def id(self):
        """Return the @id of the first graph entry."""
        return self.graph[0].get("@id") if self.graph else None

    @property
    def name(self):
        """Return the so:name of the first graph entry."""
        return self.graph[0].get("so:name") if self.graph else None

    @property
    def author(self):
        """Return the so:author of the first graph entry."""
        return self.graph[0].get("so:author") if self.graph else None

    @property
    def url(self):
        """Return the so:url of the first graph entry."""
        return self.graph[0].get("so:url") if self.graph else None

    @property
    def type(self):
        """Return the @type of the first graph entry."""
        return self.graph[0].get("@type") if self.graph else None


class JsonLdSearch(JsonLdResponse):  # pylint: disable=R0903
    """Parser for JSON-LD search view responses."""
    pass
