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
        description="Query data exports from the SLUB catalog.")

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
        "--export-format",
        default="app",
        choices=SlubFind.EXPORT_FORMATS,
        help="export format (default: app)")
    parser.add_argument(
        "--export-page",
        type=int,
        default=1369315142,
        help="export page type number (default: 1369315142)")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output (with indentation)")
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
        "query", help="search in app format")
    query_parser.add_argument("query", nargs="?", help="search query string")
    query_parser.add_argument(
        "--from-url", help="use a SLUB catalog URL as query source")
    query_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query type (default: default)")
    query_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    query_parser.add_argument(
        "--page", type=int, default=0, help="page number")
    query_parser.add_argument(
        "--count", type=int, default=0, help="results per page")
    query_parser.add_argument(
        "--sort", default="", help="sort instruction")

    # document subcommand
    doc_parser = subparsers.add_parser(
        "document", help="fetch document in app format")
    doc_parser.add_argument("document_id", help="document identifier")

    # scroll subcommand
    scroll_parser = subparsers.add_parser(
        "scroll", help="fetch all paginated results")
    scroll_parser.add_argument("query", nargs="?", help="search query string")
    scroll_parser.add_argument(
        "--from-url", help="use a SLUB catalog URL as query source")
    scroll_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query type (default: default)")
    scroll_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    scroll_parser.add_argument(
        "--batch", type=int, default=20,
        help="results per batch (default: 20)")
    scroll_parser.add_argument(
        "--sort", default="", help="sort instruction")
    scroll_parser.add_argument(
        "--stream", action="store_true",
        help="output one JSON object per line (JSONL)")

    # settings subcommand
    subparsers.add_parser(
        "settings", help="show TYPO3-find settings")

    # solr-params subcommand
    solr_params_parser = subparsers.add_parser(
        "solr-params", help="show Solr parameters for a query")
    solr_params_parser.add_argument(
        "query", nargs="?", help="search query string")
    solr_params_parser.add_argument(
        "--from-url", help="use a SLUB catalog URL as query source")
    solr_params_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query type (default: default)")
    solr_params_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    solr_params_parser.add_argument(
        "--page", type=int, default=0, help="page number")
    solr_params_parser.add_argument(
        "--count", type=int, default=0, help="results per page")
    solr_params_parser.add_argument(
        "--sort", default="", help="sort instruction")

    # solr-request subcommand
    solr_request_parser = subparsers.add_parser(
        "solr-request", help="show Solr request URL for a query")
    solr_request_parser.add_argument(
        "query", nargs="?", help="search query string")
    solr_request_parser.add_argument(
        "--from-url", help="use a SLUB catalog URL as query source")
    solr_request_parser.add_argument(
        "--type", default="default", choices=SlubFind.QUERY_TYPES,
        help="query type (default: default)")
    solr_request_parser.add_argument(
        "--facet", action="append", type=parse_facet,
        help="facet filter as KEY=VALUE (repeatable)")
    solr_request_parser.add_argument(
        "--page", type=int, default=0, help="page number")
    solr_request_parser.add_argument(
        "--count", type=int, default=0, help="results per page")
    solr_request_parser.add_argument(
        "--sort", default="", help="sort instruction")

    return parser


def make_find(args):
    """Create a SlubFind instance from parsed arguments."""
    return SlubFind(
        base_url=args.url,
        export_format=args.export_format,
        export_page=args.export_page)


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
    kwargs = dict(qtype=args.type, facet=facet, sort=args.sort)
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
    data = result.raw if hasattr(result, "raw") else result
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
            print(json_dumps(doc, pretty=args.pretty))
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
    print(json_dumps(results, pretty=args.pretty))
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
