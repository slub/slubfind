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
    assert merge_facets([("language", "ger")]) == {"language": "ger"}


def test_merge_facets_multiple():
    result = merge_facets([("language", "ger"), ("format_de14", "Buch")])
    assert result == {"language": "ger", "format_de14": "Buch"}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_result(raw):
    """Build a mock result object with a .raw attribute."""
    m = MagicMock()
    m.raw = raw
    return m


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
    find.app_search.return_value = _make_result({"docs": []})
    code = _run(["query", "python"], find, capsys)
    assert code == 0
    assert '{"docs"' in capsys.readouterr().out


def test_cmd_query_pretty(capsys):
    find = MagicMock()
    find.app_search.return_value = _make_result({"docs": []})
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
    find.app_search.return_value = None
    code = _run(["query", "python"], find, capsys)
    assert code == 1


def test_cmd_query_with_facet(capsys):
    find = MagicMock()
    find.app_search.return_value = _make_result({"docs": []})
    code = _run(["query", "--facet", "language=ger", "python"], find, capsys)
    assert code == 0
    _, kwargs = find.app_search.call_args
    assert kwargs["facet"] == {"language": "ger"}


# ---------------------------------------------------------------------------
# cmd_document
# ---------------------------------------------------------------------------

def test_cmd_document_success(capsys):
    find = MagicMock()
    find.app_document.return_value = _make_result({"id": "0-123"})
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
    find.app_document.return_value = None
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
# main — no command
# ---------------------------------------------------------------------------

def test_main_no_command():
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1
