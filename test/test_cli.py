import argparse
import io
import pytest
from unittest.mock import MagicMock, patch

from slubfind.cli import (
    build_parser,
    json_dumps,
    main,
    merge_facets,
    parse_facet,
)


# ---------------------------------------------------------------------------
# json_dumps
# ---------------------------------------------------------------------------

def test_json_dumps_default_compact():
    result = json_dumps({"a": 1})
    assert result == '{"a":1}'


def test_json_dumps_pretty():
    result = json_dumps({"a": 1}, pretty=True)
    assert '"a": 1' in result
    assert "\n" in result


def test_json_dumps_non_ascii():
    result = json_dumps({"k": "ä"})
    assert "ä" in result


# ---------------------------------------------------------------------------
# parse_facet
# ---------------------------------------------------------------------------

def test_parse_facet_valid():
    key, val = parse_facet("language=ger")
    assert key == "language"
    assert val == "ger"


def test_parse_facet_no_equals():
    with pytest.raises(argparse.ArgumentTypeError, match="KEY=VALUE"):
        parse_facet("language")


def test_parse_facet_unknown_key():
    with pytest.raises(argparse.ArgumentTypeError, match="unknown facet key"):
        parse_facet("unknown_key=value")


def test_parse_facet_valid_facet_avail():
    key, val = parse_facet("facet_avail=Online")
    assert key == "facet_avail"
    assert val == "Online"


def test_parse_facet_invalid_facet_avail():
    with pytest.raises(argparse.ArgumentTypeError, match="unknown value"):
        parse_facet("facet_avail=Invalid")


def test_parse_facet_unconstrained_accepts_any():
    key, val = parse_facet("language=ger")
    assert key == "language"
    assert val == "ger"


def test_parse_facet_all_format_de14_values():
    from slubfind.client import SlubFind
    for val in SlubFind.FACET_VALUES["format_de14"]:
        key, v = parse_facet(f"format_de14={val}")
        assert key == "format_de14"
        assert v == val


def test_parse_facet_invalid_format_de14():
    with pytest.raises(argparse.ArgumentTypeError, match="unknown value"):
        parse_facet("format_de14=Nonexistent")


def test_parse_facet_valid_access_state():
    key, val = parse_facet("access_state=open")
    assert key == "access_state"
    assert val == "open"


def test_parse_facet_invalid_access_state():
    with pytest.raises(argparse.ArgumentTypeError, match="unknown value"):
        parse_facet("access_state=invalid")


def test_parse_facet_value_with_equals():
    # value portion may itself contain '='
    key, val = parse_facet("language=a=b")
    assert key == "language"
    assert val == "a=b"


# ---------------------------------------------------------------------------
# merge_facets
# ---------------------------------------------------------------------------

def test_merge_facets_empty():
    assert merge_facets([]) is None
    assert merge_facets(None) is None


def test_merge_facets_single():
    assert merge_facets([("language", "ger")]) == [{"language": "ger"}]


def test_merge_facets_multiple():
    result = merge_facets([("language", "ger"), ("format_de14", "Buch")])
    assert result == [{"language": "ger"}, {"format_de14": "Buch"}]


def test_merge_facets_duplicate_key():
    result = merge_facets([("language", "ger"), ("language", "eng")])
    assert result == [{"language": "ger"}, {"language": "eng"}]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

EXAMPLE_URL = ("https://katalog.slub-dresden.de/"
               "?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz")


def _make_result(raw):
    """Build a mock result object with a .raw attribute."""
    m = MagicMock()
    m.raw = raw
    return m


def _mock_url_parser(is_ok=True):
    """Build a mock URLParser result."""
    p = MagicMock()
    p.is_ok = is_ok
    p.query = "manfred bonitz"
    p.qtype = "default"
    p.facets = None
    p.page = 0
    p.count = 0
    p.sort = ""
    return p


def _run(argv, find_mock, capsys):
    """Run main(), injecting find_mock via make_find patch. Returns exit code."""
    with patch("slubfind.cli.make_find", return_value=find_mock):
        with pytest.raises(SystemExit) as exc_info:
            main(argv)
    return exc_info.value.code


# ---------------------------------------------------------------------------
# cmd_query
# ---------------------------------------------------------------------------

def test_cmd_query_success(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result({"docs": []})
    code = _run(["query", "python"], find, capsys)
    assert code == 0
    assert '{"docs"' in capsys.readouterr().out


def test_cmd_query_pretty(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result({"docs": []})
    code = _run(["--pretty", "query", "python"], find, capsys)
    assert code == 0
    assert "\n" in capsys.readouterr().out


def test_cmd_query_show_url(capsys):
    find = MagicMock()
    find.url_query.return_value = "https://example.com/q"
    code = _run(["--show-url", "query", "python"], find, capsys)
    assert code == 0
    assert "https://example.com/q" in capsys.readouterr().out


def test_cmd_query_error(capsys):
    find = MagicMock()
    find.get_query.return_value = None
    code = _run(["query", "python"], find, capsys)
    assert code == 1


def test_cmd_query_with_facet(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result({"docs": []})
    code = _run(["query", "--facet", "language=ger", "python"], find, capsys)
    assert code == 0
    _, kwargs = find.get_query.call_args
    assert kwargs["facet"] == [{"language": "ger"}]


def test_cmd_query_raw_solr_response(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result({"response": {"docs": []}})
    code = _run(
        ["query", "--export-format", "raw-solr-response", "python"],
        find, capsys)
    assert code == 0


def test_cmd_query_json_solr_results(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result([{"id": "1"}])
    code = _run(
        ["query", "--export-format", "json-solr-results", "python"],
        find, capsys)
    assert code == 0
    assert '"id"' in capsys.readouterr().out


def test_cmd_query_no_facets(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result({
        "docs": [{"id": "1"}],
        "facets": {"language": {"ger": 10}}})
    code = _run(["query", "--no-facets", "python"], find, capsys)
    assert code == 0
    out = capsys.readouterr().out
    assert '"docs"' in out
    assert '"facets"' not in out


def test_cmd_query_no_facets_with_facet_counts(capsys):
    find = MagicMock()
    find.get_query.return_value = _make_result({
        "response": {"docs": []},
        "facet_counts": {"facet_fields": {}}})
    code = _run(
        ["query", "--no-facets", "--export-format", "raw-solr-response",
         "python"],
        find, capsys)
    assert code == 0
    out = capsys.readouterr().out
    assert '"response"' in out
    assert '"facet_counts"' not in out


def test_cmd_query_no_facets_non_dict(capsys):
    """--no-facets is a no-op when the result is not a dict (e.g. list)."""
    find = MagicMock()
    find.get_query.return_value = _make_result([{"id": "1"}])
    code = _run(
        ["query", "--no-facets", "--export-format", "json-solr-results",
         "python"],
        find, capsys)
    assert code == 0
    assert '"id"' in capsys.readouterr().out


# ---------------------------------------------------------------------------
# cmd_document
# ---------------------------------------------------------------------------

def test_cmd_document_success(capsys):
    find = MagicMock()
    find.get_document.return_value = _make_result({"id": "0-123"})
    code = _run(["document", "0-123"], find, capsys)
    assert code == 0
    assert '"id"' in capsys.readouterr().out


def test_cmd_document_show_url(capsys):
    find = MagicMock()
    find.url_document.return_value = "https://example.com/doc/0-123"
    code = _run(["--show-url", "document", "0-123"], find, capsys)
    assert code == 0
    assert "https://example.com/doc/0-123" in capsys.readouterr().out


def test_cmd_document_not_found(capsys):
    find = MagicMock()
    find.get_document.return_value = None
    code = _run(["document", "0-123"], find, capsys)
    assert code == 1


def test_cmd_document_show_url_none(capsys):
    find = MagicMock()
    find.url_document.return_value = None
    code = _run(["--show-url", "document", "0-123"], find, capsys)
    assert code == 1


# ---------------------------------------------------------------------------
# cmd_scroll
# ---------------------------------------------------------------------------

def test_cmd_scroll_success(capsys):
    find = MagicMock()
    find.scroll_get_query.return_value = [{"id": "1"}, {"id": "2"}]
    code = _run(["scroll", "python"], find, capsys)
    assert code == 0
    assert '"id"' in capsys.readouterr().out


def test_cmd_scroll_stream(capsys):
    find = MagicMock()
    find.stream_get_query.return_value = iter([{"id": "1"}, {"id": "2"}])
    code = _run(["scroll", "--stream", "python"], find, capsys)
    assert code == 0
    lines = [l for l in capsys.readouterr().out.splitlines() if l.strip()]
    assert len(lines) == 2


def test_cmd_scroll_show_url(capsys):
    find = MagicMock()
    find.url_query.return_value = "https://example.com/scroll"
    code = _run(["--show-url", "scroll", "python"], find, capsys)
    assert code == 0
    assert "https://example.com/scroll" in capsys.readouterr().out


def test_cmd_scroll_error(capsys):
    find = MagicMock()
    find.scroll_get_query.return_value = None
    code = _run(["scroll", "python"], find, capsys)
    assert code == 1


# ---------------------------------------------------------------------------
# cmd_settings
# ---------------------------------------------------------------------------

def test_cmd_settings_success(capsys):
    find = MagicMock()
    find.settings.return_value = {"key": "value"}
    code = _run(["settings"], find, capsys)
    assert code == 0
    assert '"key"' in capsys.readouterr().out


def test_cmd_settings_error(capsys):
    find = MagicMock()
    find.settings.return_value = None
    code = _run(["settings"], find, capsys)
    assert code == 1


# ---------------------------------------------------------------------------
# cmd_solr_params
# ---------------------------------------------------------------------------

def test_cmd_solr_params_success(capsys):
    find = MagicMock()
    find.solr_params.return_value = {"params": {"q": "python"}}
    code = _run(["solr-params", "python"], find, capsys)
    assert code == 0
    assert '"params"' in capsys.readouterr().out


def test_cmd_solr_params_error(capsys):
    find = MagicMock()
    find.solr_params.return_value = None
    code = _run(["solr-params", "python"], find, capsys)
    assert code == 1


# ---------------------------------------------------------------------------
# cmd_solr_request
# ---------------------------------------------------------------------------

def test_cmd_solr_request_success(capsys):
    find = MagicMock()
    find.solr_request.return_value = "https://solr.example.com/select?q=python"
    code = _run(["solr-request", "python"], find, capsys)
    assert code == 0
    assert "https://solr.example.com" in capsys.readouterr().out


def test_cmd_solr_request_error(capsys):
    find = MagicMock()
    find.solr_request.return_value = None
    code = _run(["solr-request", "python"], find, capsys)
    assert code == 1


# ---------------------------------------------------------------------------
# --from-url
# ---------------------------------------------------------------------------

def test_query_from_url(capsys):
    find = MagicMock()
    find.url_parser.return_value = _mock_url_parser()
    find.get_query.return_value = _make_result({"docs": []})
    code = _run(["query", "--from-url", EXAMPLE_URL], find, capsys)
    assert code == 0
    assert '"docs"' in capsys.readouterr().out


def test_query_from_url_invalid(capsys):
    find = MagicMock()
    find.url_parser.return_value = _mock_url_parser(is_ok=False)
    code = _run(["query", "--from-url", EXAMPLE_URL], find, capsys)
    assert code == 1


def test_query_from_url_show_url(capsys):
    find = MagicMock()
    find.url_parser.return_value = _mock_url_parser()
    find.url_query.return_value = "https://example.com/q"
    code = _run(
        ["--show-url", "query", "--from-url", EXAMPLE_URL], find, capsys)
    assert code == 0
    assert "https://example.com/q" in capsys.readouterr().out


def test_query_no_query_no_from_url(capsys):
    find = MagicMock()
    code = _run(["query"], find, capsys)
    assert code == 1


def test_scroll_from_url(capsys):
    find = MagicMock()
    find.url_parser.return_value = _mock_url_parser()
    find.scroll_get_query.return_value = [{"id": "1"}]
    code = _run(["scroll", "--from-url", EXAMPLE_URL], find, capsys)
    assert code == 0
    assert '"id"' in capsys.readouterr().out


def test_solr_params_from_url(capsys):
    find = MagicMock()
    find.url_parser.return_value = _mock_url_parser()
    find.solr_params.return_value = {"params": {"q": "manfred bonitz"}}
    code = _run(["solr-params", "--from-url", EXAMPLE_URL], find, capsys)
    assert code == 0
    assert '"params"' in capsys.readouterr().out


def test_solr_request_from_url(capsys):
    find = MagicMock()
    find.url_parser.return_value = _mock_url_parser()
    find.solr_request.return_value = "https://solr.example.com/select?q=test"
    code = _run(["solr-request", "--from-url", EXAMPLE_URL], find, capsys)
    assert code == 0
    assert "https://solr.example.com" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# main — no command
# ---------------------------------------------------------------------------

def test_main_no_command():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1
