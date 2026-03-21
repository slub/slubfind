"""
parser module of ``slubfind``
"""
from txpyfind.parser import JSONResponse


class HoldingStatus(JSONResponse):  # pylint: disable=R0903
    """
    Parser for holding status responses.

    Expected structure::

        {
            "access": [...],
            "additional_information": [...],
            "references": [...],
            "links": [...]
        }
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict)

    @property
    def access(self):
        """Return the access field."""
        return self.raw.get("access") if self.ok else None

    @property
    def additional_information(self):
        """Return the additional_information field."""
        return self.raw.get("additional_information") if self.ok else None

    @property
    def references(self):
        """Return the references field."""
        return self.raw.get("references") if self.ok else None

    @property
    def links(self):
        """Return the links field."""
        return self.raw.get("links") if self.ok else None


class HoldingStatusIndex(JSONResponse):  # pylint: disable=R0903
    """
    Parser for indexed holding status responses.

    Expected structure::

        {
            "status": ...,
            "location": "...",
            "links": {"isil": ..., "resource": ..., "related": ..., "count": ...}
        }
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict)

    @property
    def status(self):
        """Return the status field."""
        return self.raw.get("status") if self.ok else None

    @property
    def location(self):
        """Return the location field."""
        return self.raw.get("location") if self.ok else None

    @property
    def links(self):
        """Return the links field."""
        return self.raw.get("links") if self.ok else None


class AppDetailsRecord:
    """Lightweight wrapper around the record dict of an AppDetails response."""

    def __init__(self, raw, unescape_fn):
        self._raw = raw
        self._unescape = unescape_fn

    @property
    def raw(self):
        """Return the underlying record dict."""
        return self._raw

    def _get(self, key):
        val = self._raw.get(key)
        return self._unescape(val) if val is not None else None

    @property
    def title(self):
        """Return the title."""
        return self._get("title")

    @property
    def format(self):
        """Return the format."""
        return self._get("format")

    @property
    def contributor(self):
        """Return the contributor."""
        return self._get("contributor")

    @property
    def publisher(self):
        """Return the publisher."""
        return self._get("publisher")

    @property
    def ispartof(self):
        """Return the ispartof field."""
        return self._get("ispartof")

    @property
    def identifier(self):
        """Return the identifier."""
        return self._get("identifier")

    @property
    def language(self):
        """Return the language."""
        return self._get("language")

    @property
    def subject(self):
        """Return the subject."""
        return self._get("subject")

    @property
    def description(self):
        """Return the description."""
        return self._get("description")

    @property
    def status(self):
        """Return the status."""
        return self._get("status")

    @property
    def rvk(self):
        """Return the rvk."""
        return self._get("rvk")


class AppDetailsCopy:
    """Lightweight wrapper around a single copy dict."""

    def __init__(self, raw):
        self._raw = raw

    @property
    def raw(self):
        """Return the underlying copy dict."""
        return self._raw

    def _get(self, key):
        return self._raw.get(key)

    @property
    def barcode(self):
        """Return the barcode."""
        return self._get("barcode")

    @property
    def location(self):
        """Return the location."""
        return self._get("location")

    @property
    def location_code(self):
        """Return the location_code."""
        return self._get("location_code")

    @property
    def sublocation(self):
        """Return the sublocation."""
        return self._get("sublocation")

    @property
    def shelfmark(self):
        """Return the shelfmark."""
        return self._get("shelfmark")

    @property
    def mediatype(self):
        """Return the mediatype."""
        return self._get("mediatype")

    @property
    def status(self):
        """Return the status."""
        return self._get("status")

    @property
    def statusphrase(self):
        """Return the statusphrase."""
        return self._get("statusphrase")

    @property
    def duedate(self):
        """Return the duedate."""
        return self._get("duedate")

    @property
    def link(self):
        """Return the link."""
        return self._get("link")

    @property
    def issue(self):
        """Return the issue."""
        return self._get("issue")


class AppDetailsParts:
    """Lightweight wrapper around the parts dict."""

    def __init__(self, raw):
        self._raw = raw

    @property
    def raw(self):
        """Return the underlying parts dict."""
        return self._raw

    @property
    def title(self):
        """Return the parts title."""
        return self._raw.get("title") if isinstance(self._raw, dict) else None

    @property
    def records(self):
        """Return the parts records list."""
        if isinstance(self._raw, dict):
            return self._raw.get("records", [])
        return []


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

    @property
    def record(self):
        """Return the record as an AppDetailsRecord."""
        raw_record = self.raw.get("record") if self.ok else None
        if isinstance(raw_record, dict):
            return AppDetailsRecord(raw_record, self._unescape)
        return None

    @property
    def copies(self):
        """Return copies as a list of AppDetailsCopy."""
        raw_copies = self.raw.get("copies") if self.ok else None
        if isinstance(raw_copies, list):
            return [AppDetailsCopy(c) for c in raw_copies]
        return None

    @property
    def parts(self):
        """Return parts as AppDetailsParts."""
        raw_parts = self.raw.get("parts") if self.ok else None
        if isinstance(raw_parts, dict):
            return AppDetailsParts(raw_parts)
        return None

    @property
    def oa(self):
        """Return the oa field."""
        return self.raw.get("oa") if self.ok else None

    @property
    def thumbnail(self):
        """Return the thumbnail field."""
        return self.raw.get("thumbnail") if self.ok else None


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

    @property
    def facets(self):
        """Return the facets dict."""
        return self.raw.get("facets") if self.ok else None


class RawSolrResponse(JSONResponse):  # pylint: disable=R0903
    """
    Parser for raw-solr-response search view responses.

    Expected structure::

        {
            "response": {"numFound": ..., "start": ..., "docs": [...]},
            "facet_counts": {...},
            "highlighting": {...}
        }
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict) and "response" in self.raw
        response = self.raw.get("response", {}) if self.ok else {}
        self.num_found = response.get("numFound", 0)
        self.start = response.get("start", 0)
        self.docs = response.get("docs", [])

    @property
    def facet_counts(self):
        """Return the facet_counts dict."""
        return self.raw.get("facet_counts") if self.ok else None

    @property
    def highlighting(self):
        """Return the highlighting dict."""
        return self.raw.get("highlighting") if self.ok else None


class SolrResultsSearch(JSONResponse):  # pylint: disable=R0903
    """
    Parser for json-solr-results search view responses.

    Expected structure::

        [{field1: ..., field2: ...}, ...]
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, list)

    @property
    def docs(self):
        """Return the docs list."""
        return self.raw if self.ok else []


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
