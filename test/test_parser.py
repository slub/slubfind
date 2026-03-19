import json
import pytest
from slubfind.parser import AppDetails, AppSearch, JsonLdResponse


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
