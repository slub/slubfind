"""
parser module of ``slubfind``
"""
from txpyfind.parser import JSONResponse, RawSolrResponse, SolrResultsResponse


class HoldingStatus(JSONResponse):
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
        self.found = self.ok and any(
            key in self.raw and self.raw[key]
            for key in ("access", "additional_information", "references", "links")
        )

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


class HoldingStatusIndex(JSONResponse):
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
        self.found = self.ok and any(
            key in self.raw and self.raw[key]
            for key in ("status", "location", "links")
        )

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


class AppDetails(JSONResponse):
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


class FincDocument:
    """Lightweight wrapper around a single finc/VuFind Solr document dict."""

    def __init__(self, raw, unescape_fn):
        self._raw = raw
        self._unescape = unescape_fn

    @property
    def raw(self):
        """Return the underlying document dict."""
        return self._raw

    def _get(self, key):
        val = self._raw.get(key)
        return self._unescape(val) if val is not None else None

    def _get_list(self, key):
        val = self._raw.get(key)
        if isinstance(val, list):
            return [self._unescape(v) for v in val] if val else []
        return []

    # -- single-valued fields --

    @property
    def id(self):
        """Return the id."""
        return self._get("id")

    @property
    def title(self):
        """Return the title."""
        return self._get("title")

    @property
    def title_short(self):
        """Return the title_short."""
        return self._get("title_short")

    @property
    def title_full(self):
        """Return the title_full."""
        return self._get("title_full")

    @property
    def title_sort(self):
        """Return the title_sort."""
        return self._get("title_sort")

    @property
    def title_sub(self):
        """Return the title_sub."""
        return self._get("title_sub")

    @property
    def title_auth(self):
        """Return the title_auth."""
        return self._get("title_auth")

    @property
    def author_sort(self):
        """Return the author_sort."""
        return self._get("author_sort")

    @property
    def publishDateSort(self):  # pylint: disable=C0103
        """Return the publishDateSort."""
        return self._get("publishDateSort")

    @property
    def edition(self):
        """Return the edition."""
        return self._get("edition")

    @property
    def description(self):
        """Return the description."""
        return self._get("description")

    @property
    def imprint(self):
        """Return the imprint."""
        return self._get("imprint")

    @property
    def thumbnail(self):
        """Return the thumbnail."""
        return self._get("thumbnail")

    @property
    def record_format(self):
        """Return the record_format (Solr field: record_format)."""
        return self._get("record_format")

    @property
    def source_id(self):
        """Return the source_id."""
        return self._get("source_id")

    @property
    def record_id(self):
        """Return the record_id."""
        return self._get("record_id")

    @property
    def container_title(self):
        """Return the container_title."""
        return self._get("container_title")

    @property
    def container_volume(self):
        """Return the container_volume."""
        return self._get("container_volume")

    @property
    def container_issue(self):
        """Return the container_issue."""
        return self._get("container_issue")

    @property
    def container_start_page(self):
        """Return the container_start_page."""
        return self._get("container_start_page")

    # -- multi-valued fields --

    @property
    def author(self):
        """Return the author list."""
        return self._get_list("author")

    @property
    def author2(self):
        """Return the author2 list."""
        return self._get_list("author2")

    @property
    def author_corporate(self):
        """Return the author_corporate list."""
        return self._get_list("author_corporate")

    @property
    def author_role(self):
        """Return the author_role list."""
        return self._get_list("author_role")

    @property
    def author_id(self):
        """Return the author_id list."""
        return self._get_list("author_id")

    @property
    def format(self):
        """Return the format list."""
        return self._get_list("format")

    @property
    def language(self):
        """Return the language list."""
        return self._get_list("language")

    @property
    def publisher(self):
        """Return the publisher list."""
        return self._get_list("publisher")

    @property
    def publishDate(self):  # pylint: disable=C0103
        """Return the publishDate list."""
        return self._get_list("publishDate")

    @property
    def isbn(self):
        """Return the isbn list."""
        return self._get_list("isbn")

    @property
    def issn(self):
        """Return the issn list."""
        return self._get_list("issn")

    @property
    def url(self):
        """Return the url list."""
        return self._get_list("url")

    @property
    def topic(self):
        """Return the topic list."""
        return self._get_list("topic")

    @property
    def topic_facet(self):
        """Return the topic_facet list."""
        return self._get_list("topic_facet")

    @property
    def series(self):
        """Return the series list."""
        return self._get_list("series")

    @property
    def series2(self):
        """Return the series2 list."""
        return self._get_list("series2")

    @property
    def contents(self):
        """Return the contents list."""
        return self._get_list("contents")

    @property
    def genre(self):
        """Return the genre list."""
        return self._get_list("genre")

    @property
    def geographic(self):
        """Return the geographic list."""
        return self._get_list("geographic")

    @property
    def institution(self):
        """Return the institution list."""
        return self._get_list("institution")

    @property
    def collection(self):
        """Return the collection list."""
        return self._get_list("collection")

    @property
    def building(self):
        """Return the building list."""
        return self._get_list("building")

    @property
    def mega_collection(self):
        """Return the mega_collection list."""
        return self._get_list("mega_collection")

    @property
    def rvk_facet(self):
        """Return the rvk_facet list."""
        return self._get_list("rvk_facet")

    @property
    def signatur(self):
        """Return the signatur list."""
        return self._get_list("signatur")

    @property
    def barcode(self):
        """Return the barcode list."""
        return self._get_list("barcode")


class FincSolrResponse(RawSolrResponse):
    """RawSolrResponse with docs wrapped as FincDocument instances."""

    def __init__(self, plain):
        super().__init__(plain)
        self.docs = [FincDocument(d, self._unescape) for d in self.docs]


class FincSolrResults(SolrResultsResponse):  # pylint: disable=R0903
    """SolrResultsResponse with docs wrapped as FincDocument instances."""

    @property
    def docs(self):
        """Return docs wrapped as FincDocument instances."""
        return [FincDocument(d, self._unescape) for d in super().docs]


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


class JsonLdDetails(JsonLdResponse):
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
