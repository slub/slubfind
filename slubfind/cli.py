"""
command-line interface of ``slubfind`` package
"""
import argparse
import json
import logging
import os
import sys

from . import __version__
from .client import SlubFind
from txpyfind.parser import JSONResponse

logger = logging.getLogger(__name__)


def parse_facet(value):
    """Parse a KEY=VALUE facet argument into a (key, value) tuple."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"facet must be in KEY=VALUE format, got: {value}")
    key, val = value.split("=", 1)
    if key not in SlubFind.FACETS:
        valid = ", ".join(SlubFind.FACETS)
        raise argparse.ArgumentTypeError(
            f"unknown facet key {key!r}, choose from: {valid}")
    if key in SlubFind.FACET_VALUES:
        allowed = SlubFind.FACET_VALUES[key]
        if val not in allowed:
            raise argparse.ArgumentTypeError(
                f"unknown value {val!r} for facet {key!r}, "
                f"choose from: {', '.join(allowed)}")
    return key, val


def merge_facets(facet_list):
    """Convert a list of (key, value) tuples into a list of single-key dicts."""
    if not facet_list:
        return None
    return [{k: v} for k, v in facet_list]


def json_dumps(obj, pretty=False):
    """Serialize object to JSON string."""
    if pretty:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def build_parser():
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="slubfind",
        description=(
            "Query records and export endpoints from the SLUB catalog. "
            "Use query for result lists, document for one record, and "
            "scroll for complete result sets."
        ),
        epilog=(
            "examples:\n"
            "  slubfind query \"manfred bonitz\"\n"
            "  slubfind document 0-1132486122 --export-format json-ld\n"
            "  slubfind scroll \"open access\" --stream\n"
            "  slubfind --show-url query --from-url "
            "\"https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--url",
        default=os.environ.get(
            "SLUBFIND_URL", "https://katalog.slub-dresden.de"),
        help="base URL of the SLUB catalog"
             " (or set SLUBFIND_URL env var,"
             " default: https://katalog.slub-dresden.de)")
    parser.add_argument(
        "--export-page",
        type=int,
        default=1369315142,
        help="export page type number (default: 1369315142)")
    parser.add_argument(
        "--show-url",
        action="store_true",
        help="print the request URL instead of fetching the response")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="enable debug logging to stderr")

    subparsers = parser.add_subparsers(dest="command")

    # query subcommand
    query_parser = subparsers.add_parser(
        "query",
        help="search catalog records",
        description=(
            "Search the catalog and return one page of results. "
            "The default export format is 'app', a compact JSON result set "
            "used by the SLUB app and suitable for general scripting."
        ),
        epilog=(
            "examples:\n"
            "  slubfind query \"manfred bonitz\"\n"
            "  slubfind query \"manfred bonitz\" --facet \"format_de14=Book, E-Book\"\n"
            "  slubfind query \"manfred bonitz\" --export-format json-solr-results\n"
            "  slubfind query --from-url "
            "\"https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    query_parser.add_argument("query", nargs="?", help="search query string")
    query_parser.add_argument(
        "--from-url",
        help="parse query parameters from a SLUB catalog URL instead")
    query_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query field to search (default: default)")
    query_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE; can be repeated")
    query_parser.add_argument(
        "--page", type=int, default=0, help="zero-based result page number")
    query_parser.add_argument(
        "--count", type=int, default=0,
        help="results per page; 0 uses the catalog default")
    query_parser.add_argument(
        "--sort", default="",
        help="sort instruction, for example 'publishDateSort desc'")
    query_parser.add_argument(
        "--export-format",
        default="app",
        choices=SlubFind.QUERY_EXPORT_FORMATS,
        help=(
            "output format: app (compact app JSON), json-ld (linked data), "
            "json-solr-results (Solr docs only), raw-solr-response "
            "(complete Solr response); default: app"))
    query_parser.add_argument(
        "--no-facets",
        action="store_true",
        help="omit facet data from the JSON output")
    query_parser.add_argument(
        "--no-parser",
        action="store_true",
        help="skip response parsing and print raw server output")
    query_parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output")

    # document subcommand
    doc_parser = subparsers.add_parser(
        "document",
        help="fetch one record by catalog ID",
        description=(
            "Fetch one document record by ID. The default export format is "
            "'app', a structured detail view with record metadata, copies, "
            "and multipart information when available."
        ),
        epilog=(
            "examples:\n"
            "  slubfind document 0-1132486122\n"
            "  slubfind document 0-1132486122 --export-format json-ld\n"
            "  slubfind document 0-320589099 --export-format json-holding-status\n"
            "  slubfind document 0-1809383722 --export-format json-holding-status-index"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    doc_parser.add_argument(
        "document_id",
        help="catalog document identifier, for example 0-1132486122")
    doc_parser.add_argument(
        "--export-format",
        default="app",
        choices=SlubFind.DOCUMENT_EXPORT_FORMATS,
        help=(
            "output format: app (detail JSON), json-ld (linked data), "
            "json-holding-status (links and references), "
            "json-holding-status-index (availability summary and links); "
            "default: app"))
    doc_parser.add_argument(
        "--no-parser",
        action="store_true",
        help="skip response parsing and print raw server output")
    doc_parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output")

    # scroll subcommand
    scroll_parser = subparsers.add_parser(
        "scroll",
        help="fetch all records for a query",
        description=(
            "Fetch the full result set by paging through the catalog until "
            "all matching records have been retrieved. This command always "
            "uses the raw Solr export internally."
        ),
        epilog=(
            "examples:\n"
            "  slubfind scroll \"manfred bonitz\"\n"
            "  slubfind scroll \"manfred bonitz\" --batch 100\n"
            "  slubfind scroll \"manfred bonitz\" --stream | jq .id"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    scroll_parser.add_argument("query", nargs="?", help="search query string")
    scroll_parser.add_argument(
        "--from-url",
        help="parse query parameters from a SLUB catalog URL instead")
    scroll_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query field to search (default: default)")
    scroll_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE; can be repeated")
    scroll_parser.add_argument(
        "--batch", type=int, default=20,
        help="number of records to fetch per request (default: 20)")
    scroll_parser.add_argument(
        "--sort", default="",
        help="sort instruction, for example 'publishDateSort desc'")
    scroll_parser.add_argument(
        "--stream", action="store_true",
        help="print one JSON object per line instead of one JSON array")

    # settings subcommand
    settings_parser = subparsers.add_parser(
        "settings",
        help="show TYPO3-find settings",
        description=(
            "Fetch the TYPO3-find settings exposed by the catalog export "
            "endpoint."
        ))
    settings_parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output")

    # solr-params subcommand
    solr_params_parser = subparsers.add_parser(
        "solr-params",
        help="show Solr parameters for a query",
        description=(
            "Resolve a catalog query to the parameter set sent to Solr. "
            "Useful for debugging and comparing TYPO3-find behavior."
        ),
        epilog=(
            "examples:\n"
            "  slubfind solr-params \"manfred bonitz\"\n"
            "  slubfind solr-params --from-url "
            "\"https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    solr_params_parser.add_argument(
        "query", nargs="?", help="search query string")
    solr_params_parser.add_argument(
        "--from-url",
        help="parse query parameters from a SLUB catalog URL instead")
    solr_params_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query field to search (default: default)")
    solr_params_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE; can be repeated")
    solr_params_parser.add_argument(
        "--page", type=int, default=0, help="zero-based result page number")
    solr_params_parser.add_argument(
        "--count", type=int, default=0,
        help="results per page; 0 uses the catalog default")
    solr_params_parser.add_argument(
        "--sort", default="",
        help="sort instruction, for example 'publishDateSort desc'")
    solr_params_parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output")

    # solr-request subcommand
    solr_request_parser = subparsers.add_parser(
        "solr-request",
        help="show the Solr request URL for a query",
        description=(
            "Resolve a catalog query to the Solr request URL generated by "
            "TYPO3-find."
        ),
        epilog=(
            "examples:\n"
            "  slubfind solr-request \"manfred bonitz\"\n"
            "  slubfind solr-request --from-url "
            "\"https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    solr_request_parser.add_argument(
        "query", nargs="?", help="search query string")
    solr_request_parser.add_argument(
        "--from-url",
        help="parse query parameters from a SLUB catalog URL instead")
    solr_request_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query field to search (default: default)")
    solr_request_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE; can be repeated")
    solr_request_parser.add_argument(
        "--page", type=int, default=0, help="zero-based result page number")
    solr_request_parser.add_argument(
        "--count", type=int, default=0,
        help="results per page; 0 uses the catalog default")
    solr_request_parser.add_argument(
        "--sort", default="",
        help="sort instruction, for example 'publishDateSort desc'")

    return parser


def make_find(args):
    """Create a SlubFind instance from parsed arguments."""
    return SlubFind(
        base_url=args.url,
        export_format=getattr(args, "export_format", "app"),
        export_page=args.export_page,
        parser_class=None if getattr(args, "no_parser", False) else JSONResponse)


def resolve_from_url(find, args):
    """Resolve --from-url into query parameters on args.

    Returns True on success, False on error. When --from-url is not
    set, validates that a positional query was provided instead.
    """
    if not args.from_url:
        if args.query is None:
            print("error: either query or --from-url is required",
                  file=sys.stderr)
            return False
        return True
    parsed = find.url_parser(args.from_url)
    if not parsed.is_ok:
        print("error: could not parse URL", file=sys.stderr)
        return False
    args.query = parsed.query
    args.type = parsed.qtype
    args.facet = parsed.facets
    if hasattr(args, "page"):
        args.page = parsed.page
    if hasattr(args, "count"):
        args.count = parsed.count
    args.sort = parsed.sort
    return True


def query_kwargs(args):
    """Build keyword arguments for query methods from parsed args."""
    facet = args.facet if args.from_url else merge_facets(args.facet)
    kwargs = {"qtype": args.type, "facet": facet, "sort": args.sort}
    if hasattr(args, "page"):
        kwargs["page"] = args.page
    if hasattr(args, "count"):
        kwargs["count"] = args.count
    return kwargs


def cmd_query(find, args):
    """Handle the query subcommand."""
    if not resolve_from_url(find, args):
        return 1
    kwargs = query_kwargs(args)
    if args.show_url:
        print(find.url_query(args.query, **kwargs))
        return 0
    result = find.get_query(args.query, **kwargs)
    if result is None:
        print("error: no results", file=sys.stderr)
        return 1
    if args.no_parser:
        print(result.plain if hasattr(result, "plain") else result)
        return 0
    data = result.raw if hasattr(result, "raw") else result
    if args.no_facets and isinstance(data, dict):
        data = {k: v for k, v in data.items()
                if k not in ("facets", "facet_counts")}
    print(json_dumps(data, pretty=args.pretty))
    return 0


def cmd_document(find, args):
    """Handle the document subcommand."""
    if args.show_url:
        url = find.url_document(args.document_id)
        if url is None:
            print("error: could not build document URL", file=sys.stderr)
            return 1
        print(url)
        return 0
    result = find.get_document(args.document_id)
    if result is None:
        print("error: document not found", file=sys.stderr)
        return 1
    if args.no_parser:
        print(result.plain if hasattr(result, "plain") else result)
        return 0
    data = result.raw if hasattr(result, "raw") else result
    print(json_dumps(data, pretty=args.pretty))
    return 0


def cmd_scroll(find, args):
    """Handle the scroll subcommand."""
    if not resolve_from_url(find, args):
        return 1
    facet = args.facet if args.from_url else merge_facets(args.facet)
    if args.show_url:
        print(find.url_query(
            args.query,
            qtype=args.type,
            facet=facet,
            count=args.batch,
            sort=args.sort))
        return 0
    if args.stream:
        for doc in find.stream_get_query(
                args.query,
                qtype=args.type,
                facet=facet,
                batch=args.batch,
                sort=args.sort):
            print(json_dumps(doc))
        return 0

    results = find.scroll_get_query(
        args.query,
        qtype=args.type,
        facet=facet,
        batch=args.batch,
        sort=args.sort)
    if results is None:
        print("error: no results", file=sys.stderr)
        return 1
    print(json_dumps(results))
    return 0


def cmd_settings(find, args):
    """Handle the settings subcommand."""
    result = find.settings()
    if result is None:
        print("error: could not retrieve settings", file=sys.stderr)
        return 1
    print(json_dumps(result, pretty=args.pretty))
    return 0


def cmd_solr_params(find, args):
    """Handle the solr-params subcommand."""
    if not resolve_from_url(find, args):
        return 1
    kwargs = query_kwargs(args)
    result = find.solr_params(args.query, **kwargs)
    if result is None:
        print("error: could not retrieve Solr parameters", file=sys.stderr)
        return 1
    print(json_dumps(result, pretty=args.pretty))
    return 0


def cmd_solr_request(find, args):
    """Handle the solr-request subcommand."""
    if not resolve_from_url(find, args):
        return 1
    kwargs = query_kwargs(args)
    result = find.solr_request(args.query, **kwargs)
    if result is None:
        print("error: could not retrieve Solr request URL", file=sys.stderr)
        return 1
    print(result)
    return 0


def main(argv=None):
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            stream=sys.stderr,
            format="%(levelname)s: %(name)s: %(message)s")

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    find = make_find(args)

    commands = {
        "query": cmd_query,
        "document": cmd_document,
        "scroll": cmd_scroll,
        "settings": cmd_settings,
        "solr-params": cmd_solr_params,
        "solr-request": cmd_solr_request,
    }
    sys.exit(commands[args.command](find, args))
