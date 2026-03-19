import json
import pytest
from slubfind.parser import AppDetails


def _make(data):
    """Build an AppDetails from a Python object (serialised to JSON)."""
    return AppDetails(json.dumps(data))


def test_ok_and_found_with_valid_id():
    result = _make({"id": "0-1132486122"})
    assert result.ok is True
    assert result.found is True


def test_ok_but_not_found_empty_id():
    result = _make({"id": ""})
    assert result.ok is True
    assert result.found is False


def test_ok_but_not_found_whitespace_id():
    result = _make({"id": "   "})
    assert result.ok is True
    assert result.found is False


def test_not_ok_missing_id():
    result = _make({"title": "something"})
    assert result.ok is False
    assert result.found is False


def test_not_ok_non_dict_response():
    result = _make(["item1", "item2"])
    assert result.ok is False
    assert result.found is False


def test_not_ok_null_response():
    result = AppDetails("null")
    assert result.ok is False
    assert result.found is False


def test_ok_but_not_found_numeric_id():
    # id present but not a string — ok (key exists) but not found
    result = _make({"id": 42})
    assert result.ok is True
    assert result.found is False


def test_invalid_json_gives_none_raw():
    result = AppDetails("not-json{{{")
    assert result.raw is None
    assert result.ok is False
    assert result.found is False
