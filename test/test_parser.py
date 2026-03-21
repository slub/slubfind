import json
import pytest
from slubfind.parser import (
    AppDetails, AppDetailsCopy, AppDetailsParts, AppDetailsRecord,
    AppSearch, HoldingStatus, HoldingStatusIndex,
    JsonLdResponse, JsonLdDetails, JsonLdSearch,
    RawSolrResponse, SolrResultsSearch
)


def _make(cls, data):
    """Build a parser instance from a Python object (serialised to JSON)."""
    return cls(json.dumps(data))


# ---------------------------------------------------------------------------
# AppDetailsRecord
# ---------------------------------------------------------------------------

def test_app_details_record_properties():
    def noop(v):
        return v
    rec = AppDetailsRecord(
        {"title": "T", "format": "Book", "contributor": "A",
         "publisher": "P", "ispartof": "S", "identifier": "I",
         "language": "eng", "subject": "S", "description": "D",
         "status": "available", "rvk": "AB 123"},
        noop)
    assert rec.title == "T"
    assert rec.format == "Book"
    assert rec.contributor == "A"
    assert rec.publisher == "P"
    assert rec.ispartof == "S"
    assert rec.identifier == "I"
    assert rec.language == "eng"
    assert rec.subject == "S"
    assert rec.description == "D"
    assert rec.status == "available"
    assert rec.rvk == "AB 123"
    assert rec.raw == {"title": "T", "format": "Book", "contributor": "A",
                       "publisher": "P", "ispartof": "S", "identifier": "I",
                       "language": "eng", "subject": "S", "description": "D",
                       "status": "available", "rvk": "AB 123"}


def test_app_details_record_unescape():
    import html
    rec = AppDetailsRecord(
        {"title": "M&uuml;nchen &amp; Berlin"},
        html.unescape)
    assert rec.title == "München & Berlin"


def test_app_details_record_missing_key():
    def noop(v):
        return v
    rec = AppDetailsRecord({}, noop)
    assert rec.title is None
    assert rec.format is None


# ---------------------------------------------------------------------------
# AppDetailsCopy
# ---------------------------------------------------------------------------

def test_app_details_copy_properties():
    copy = AppDetailsCopy({
        "barcode": "123", "location": "Main", "location_code": "ML",
        "sublocation": "2F", "shelfmark": "AB 1", "mediatype": "book",
        "status": "available", "statusphrase": "Available",
        "duedate": "2026-04-01", "link": "https://example.com",
        "issue": "Vol. 1"})
    assert copy.barcode == "123"
    assert copy.location == "Main"
    assert copy.location_code == "ML"
    assert copy.sublocation == "2F"
    assert copy.shelfmark == "AB 1"
    assert copy.mediatype == "book"
    assert copy.status == "available"
    assert copy.statusphrase == "Available"
    assert copy.duedate == "2026-04-01"
    assert copy.link == "https://example.com"
    assert copy.issue == "Vol. 1"
    assert copy.raw["barcode"] == "123"


def test_app_details_copy_missing_key():
    copy = AppDetailsCopy({})
    assert copy.barcode is None
    assert copy.status is None


# ---------------------------------------------------------------------------
# AppDetailsParts
# ---------------------------------------------------------------------------

def test_app_details_parts_title_and_records():
    parts = AppDetailsParts({
        "title": "Mehrbändiges Werk",
        "records": [
            {"id": "0-1", "name": "Vol 1", "part": "1",
             "author": "A", "imprint": "2020"}
        ]})
    assert parts.title == "Mehrbändiges Werk"
    assert len(parts.records) == 1
    assert parts.records[0]["id"] == "0-1"
    assert parts.raw["title"] == "Mehrbändiges Werk"


def test_app_details_parts_empty():
    parts = AppDetailsParts({})
    assert parts.title is None
    assert parts.records == []


def test_app_details_parts_non_dict():
    parts = AppDetailsParts("not a dict")
    assert parts.title is None
    assert parts.records == []


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


def test_app_details_record_returns_wrapper():
    result = _make(AppDetails, {
        "id": "0-123",
        "record": {"title": "Test Title", "format": "Book"}})
    rec = result.record
    assert isinstance(rec, AppDetailsRecord)
    assert rec.title == "Test Title"
    assert rec.format == "Book"


def test_app_details_record_none_when_missing():
    result = _make(AppDetails, {"id": "0-123"})
    assert result.record is None


def test_app_details_unescape_html_entities():
    result = _make(AppDetails, {
        "id": "0-123",
        "record": {"title": "M&uuml;nchen &amp; Berlin"}})
    assert result.record.title == "München & Berlin"


def test_app_details_copies_returns_wrappers():
    result = _make(AppDetails, {
        "id": "0-123",
        "copies": [
            {"barcode": "111", "location": "Main"},
            {"barcode": "222", "location": "Branch"}
        ]})
    copies = result.copies
    assert len(copies) == 2
    assert isinstance(copies[0], AppDetailsCopy)
    assert copies[0].barcode == "111"
    assert copies[1].location == "Branch"


def test_app_details_copies_none_when_missing():
    result = _make(AppDetails, {"id": "0-123"})
    assert result.copies is None


def test_app_details_parts_returns_wrapper():
    result = _make(AppDetails, {
        "id": "0-123",
        "parts": {"title": "MW", "records": []}})
    parts = result.parts
    assert isinstance(parts, AppDetailsParts)
    assert parts.title == "MW"


def test_app_details_parts_none_when_missing():
    result = _make(AppDetails, {"id": "0-123"})
    assert result.parts is None


def test_app_details_oa_and_thumbnail():
    result = _make(AppDetails, {
        "id": "0-123", "oa": 1, "thumbnail": "https://example.com/img.jpg"})
    assert result.oa == 1
    assert result.thumbnail == "https://example.com/img.jpg"


def test_app_details_oa_and_thumbnail_missing():
    result = _make(AppDetails, {"id": "0-123"})
    assert result.oa is None
    assert result.thumbnail is None


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


def test_app_search_facets_present():
    result = _make(AppSearch, {
        "docs": [], "facets": {"language": {"ger": 10}}})
    assert result.facets == {"language": {"ger": 10}}


def test_app_search_facets_absent():
    result = _make(AppSearch, {"docs": []})
    assert result.facets is None


def test_app_search_facets_not_ok():
    result = _make(AppSearch, {"numFound": 0})
    assert result.facets is None


# ---------------------------------------------------------------------------
# RawSolrResponse
# ---------------------------------------------------------------------------

def test_raw_solr_response_ok():
    result = _make(RawSolrResponse, {
        "response": {"numFound": 10, "start": 0, "docs": [{"id": "1"}]},
        "facet_counts": {"facet_fields": {}},
        "highlighting": {"1": {}}})
    assert result.ok is True
    assert result.num_found == 10
    assert result.start == 0
    assert result.docs == [{"id": "1"}]
    assert result.facet_counts == {"facet_fields": {}}
    assert result.highlighting == {"1": {}}


def test_raw_solr_response_missing_response_key():
    result = _make(RawSolrResponse, {"other": "data"})
    assert result.ok is False
    assert result.num_found == 0
    assert result.start == 0
    assert result.docs == []
    assert result.facet_counts is None
    assert result.highlighting is None


def test_raw_solr_response_minimal():
    result = _make(RawSolrResponse, {"response": {}})
    assert result.ok is True
    assert result.num_found == 0
    assert result.docs == []
    assert result.facet_counts is None
    assert result.highlighting is None


def test_raw_solr_response_invalid_json():
    result = RawSolrResponse("not-json{{{")
    assert result.ok is False


# ---------------------------------------------------------------------------
# SolrResultsSearch
# ---------------------------------------------------------------------------

def test_solr_results_search_valid_list():
    result = _make(SolrResultsSearch, [{"id": "1"}, {"id": "2"}])
    assert result.ok is True
    assert result.docs == [{"id": "1"}, {"id": "2"}]


def test_solr_results_search_empty_list():
    result = _make(SolrResultsSearch, [])
    assert result.ok is True
    assert result.docs == []


def test_solr_results_search_non_list():
    result = _make(SolrResultsSearch, {"not": "a list"})
    assert result.ok is False
    assert result.docs == []


def test_solr_results_search_invalid_json():
    result = SolrResultsSearch("not-json{{{")
    assert result.ok is False
    assert result.docs == []


# ---------------------------------------------------------------------------
# HoldingStatus
# ---------------------------------------------------------------------------

def test_holding_status_ok():
    result = _make(HoldingStatus, {
        "access": ["loan"],
        "additional_information": [{"url": "https://example.com",
                                    "label": "Link", "type": "info"}],
        "references": ["ref1"],
        "links": ["link1"]})
    assert result.ok is True
    assert result.access == ["loan"]
    assert result.additional_information[0]["url"] == "https://example.com"
    assert result.references == ["ref1"]
    assert result.links == ["link1"]


def test_holding_status_not_ok():
    result = _make(HoldingStatus, ["not", "a", "dict"])
    assert result.ok is False
    assert result.access is None
    assert result.additional_information is None
    assert result.references is None
    assert result.links is None


def test_holding_status_missing_fields():
    result = _make(HoldingStatus, {})
    assert result.ok is True
    assert result.access is None
    assert result.additional_information is None


# ---------------------------------------------------------------------------
# HoldingStatusIndex
# ---------------------------------------------------------------------------

def test_holding_status_index_ok():
    result = _make(HoldingStatusIndex, {
        "status": "available",
        "location": "Main Library",
        "links": {"isil": "DE-14", "resource": [], "related": [],
                  "count": 1}})
    assert result.ok is True
    assert result.status == "available"
    assert result.location == "Main Library"
    assert result.links["isil"] == "DE-14"
    assert result.links["count"] == 1


def test_holding_status_index_not_ok():
    result = _make(HoldingStatusIndex, ["not", "a", "dict"])
    assert result.ok is False
    assert result.status is None
    assert result.location is None
    assert result.links is None


def test_holding_status_index_missing_fields():
    result = _make(HoldingStatusIndex, {})
    assert result.ok is True
    assert result.status is None
    assert result.location is None


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
