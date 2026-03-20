import json
import pytest
from slubfind.parser import (
    AppDetails, AppSearch, JsonLdResponse, JsonLdDetails, JsonLdSearch
)


def _make(cls, data):
    """Build a parser instance from a Python object (serialised to JSON)."""
    return cls(json.dumps(data))


# ---------------------------------------------------------------------------
# AppDetails
# ---------------------------------------------------------------------------

def test_app_details_ok_and_found_with_valid_id():
    result = _make(AppDetails, {"id": "0-1132486122"})
    assert result.ok is True
    assert result.found is True


def test_app_details_ok_but_not_found_empty_id():
    result = _make(AppDetails, {"id": ""})
    assert result.ok is True
    assert result.found is False


def test_app_details_ok_but_not_found_whitespace_id():
    result = _make(AppDetails, {"id": "   "})
    assert result.ok is True
    assert result.found is False


def test_app_details_not_ok_missing_id():
    result = _make(AppDetails, {"title": "something"})
    assert result.ok is False
    assert result.found is False


def test_app_details_not_ok_non_dict_response():
    result = _make(AppDetails, ["item1", "item2"])
    assert result.ok is False
    assert result.found is False


def test_app_details_not_ok_null_response():
    result = AppDetails("null")
    assert result.ok is False
    assert result.found is False


def test_app_details_ok_but_not_found_numeric_id():
    result = _make(AppDetails, {"id": 42})
    assert result.ok is True
    assert result.found is False


def test_app_details_invalid_json():
    result = AppDetails("not-json{{{")
    assert result.raw is None
    assert result.ok is False
    assert result.found is False


def test_app_details_id_field():
    result = _make(AppDetails, {"id": "0-1132486122"})
    assert result.id == "0-1132486122"


def test_app_details_record_property():
    result = _make(AppDetails, {
        "id": "0-123",
        "record": {"title": "Test Title", "format": "Book"}})
    assert result.record == {"title": "Test Title", "format": "Book"}
    assert result.title == "Test Title"
    assert result.format == "Book"


def test_app_details_record_none_when_missing():
    result = _make(AppDetails, {"id": "0-123"})
    assert result.record is None
    assert result.title is None


def test_app_details_unescape_html_entities():
    result = _make(AppDetails, {
        "id": "0-123",
        "record": {"title": "M&uuml;nchen &amp; Berlin"}})
    assert result.record["title"] == "München & Berlin"
    assert result.title == "München & Berlin"


def test_app_details_convenience_properties():
    result = _make(AppDetails, {
        "id": "0-123",
        "record": {
            "title": "A Title",
            "format": "Book",
            "contributor": "Author Name",
            "identifier": "ISBN-123"}})
    assert result.contributor == "Author Name"
    assert result.identifier == "ISBN-123"


# ---------------------------------------------------------------------------
# AppSearch
# ---------------------------------------------------------------------------

def test_app_search_ok():
    result = _make(AppSearch, {
        "numFound": 5, "start": 0, "docs": [{"id": "1"}], "facets": {}})
    assert result.ok is True
    assert result.num_found == 5
    assert result.start == 0
    assert result.docs == [{"id": "1"}]


def test_app_search_ok_minimal():
    result = _make(AppSearch, {"docs": []})
    assert result.ok is True
    assert result.num_found == 0
    assert result.start == 0
    assert result.docs == []


def test_app_search_not_ok_missing_docs():
    result = _make(AppSearch, {"numFound": 0})
    assert result.ok is False
    assert result.num_found == 0
    assert result.docs == []


def test_app_search_not_ok_non_dict():
    result = _make(AppSearch, ["item"])
    assert result.ok is False


def test_app_search_invalid_json():
    result = AppSearch("not-json{{{")
    assert result.raw is None
    assert result.ok is False
    assert result.num_found == 0
    assert result.docs == []


# ---------------------------------------------------------------------------
# JsonLdResponse
# ---------------------------------------------------------------------------

def test_jsonld_ok_with_graph():
    result = _make(JsonLdResponse, {
        "@context": {"so": "http://schema.org/"},
        "@graph": [
            {"@id": "https://example.com/id/0-123",
             "so:name": "Test", "@type": "so:Book"}
        ]})
    assert result.ok is True
    assert len(result.graph) == 1
    assert result.graph[0]["@type"] == "so:Book"


def test_jsonld_ok_empty_graph():
    result = _make(JsonLdResponse, {
        "@context": {"so": "http://schema.org/"}, "@graph": []})
    assert result.ok is True
    assert result.graph == []


def test_jsonld_ok_no_graph_key():
    result = _make(JsonLdResponse, {
        "@context": {"so": "http://schema.org/"}})
    assert result.ok is True
    assert result.graph == []


def test_jsonld_not_ok_missing_context():
    result = _make(JsonLdResponse, {"@graph": []})
    assert result.ok is False
    assert result.graph == []


def test_jsonld_not_ok_non_dict():
    result = _make(JsonLdResponse, ["item"])
    assert result.ok is False


def test_jsonld_invalid_json():
    result = JsonLdResponse("not-json{{{")
    assert result.raw is None
    assert result.ok is False
    assert result.graph == []


# ---------------------------------------------------------------------------
# JsonLdDetails
# ---------------------------------------------------------------------------

def test_jsonld_details_found_with_real_id():
    result = _make(JsonLdDetails, {
        "@context": {"so": "http://schema.org/"},
        "@graph": [
            {"@id": "https://katalog.slub-dresden.de/id/0-123",
             "so:name": "Test Book", "so:author": "Author",
             "so:url": "https://example.com", "@type": "so:Book"}
        ]})
    assert result.ok is True
    assert result.found is True
    assert result.id == "https://katalog.slub-dresden.de/id/0-123"
    assert result.name == "Test Book"
    assert result.author == "Author"
    assert result.url == "https://example.com"
    assert result.type == "so:Book"


def test_jsonld_details_not_found_bare_id():
    result = _make(JsonLdDetails, {
        "@context": {"so": "http://schema.org/"},
        "@graph": [
            {"@id": "https://katalog.slub-dresden.de/id/",
             "so:name": "Not Found"}
        ]})
    assert result.ok is True
    assert result.found is False


def test_jsonld_details_not_found_bare_id_no_trailing_slash():
    result = _make(JsonLdDetails, {
        "@context": {"so": "http://schema.org/"},
        "@graph": [
            {"@id": "https://katalog.slub-dresden.de/id",
             "so:name": "Not Found"}
        ]})
    assert result.ok is True
    assert result.found is False


def test_jsonld_details_not_found_empty_graph():
    result = _make(JsonLdDetails, {
        "@context": {"so": "http://schema.org/"},
        "@graph": []})
    assert result.ok is True
    assert result.found is False


def test_jsonld_details_properties_empty_graph():
    result = _make(JsonLdDetails, {
        "@context": {"so": "http://schema.org/"},
        "@graph": []})
    assert result.id is None
    assert result.name is None
    assert result.author is None
    assert result.url is None
    assert result.type is None


# ---------------------------------------------------------------------------
# JsonLdSearch
# ---------------------------------------------------------------------------

def test_jsonld_search_ok():
    result = _make(JsonLdSearch, {
        "@context": {"so": "http://schema.org/"},
        "@graph": [
            {"@id": "https://example.com/1", "so:name": "Result 1"},
            {"@id": "https://example.com/2", "so:name": "Result 2"}
        ]})
    assert result.ok is True
    assert len(result.graph) == 2


def test_jsonld_search_not_ok():
    result = _make(JsonLdSearch, {"data": "invalid"})
    assert result.ok is False
    assert result.graph == []
