import re
from txpyfind import utils
from txpyfind.client import Find

from .parser import AppDetails


class SlubFind(Find):

    def __init__(self,
                 base_url="https://katalog.slub-dresden.de",
                 document_path="id",
                 query_types=[
                     "default",
                     "author",
                     "title",
                     "topic",
                     "barcode",
                     "ident",
                     "rvk_facet",
                     "signatur",
                     "imprint",
                     "series2"
                     ],
                 facets=[
                     "facet_avail",
                     "format_de14",
                     "publishDateSort",
                     "branch_collcode",
                     "branch",
                     "language",
                     "thema",
                     "author",
                     "facet_music_notation_de14",
                     "music_heading_browse",
                     "mega_collection"
                     ],
                 count_limit=1000,
                 sort_pattern=re.compile(r"^(score|publishDateSort|title_sort|id)[+ ](asc|desc)$"),
                 export_format="app",
                 export_page=1369315142):
        super().__init__(base_url,
                         document_path=document_path,
                         query_types=query_types,
                         facets=facets,
                         count_limit=count_limit,
                         sort_pattern=sort_pattern,
                         export_format=export_format,
                         export_page=export_page)

    def app_details(self, document_id, type_num=None):
        return self.get_document(document_id, data_format="app", type_num=type_num, parser_class=AppDetails)

    def app_search(self, query, qtype="default", facet={}, page=0, count=0, sort="", type_num=None):
        return self.get_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="app", type_num=type_num)

    def settings(self, query="qqqqq", qtype="default", facet={}, page=0, count=0, sort="", type_num=None):
        result = self.get_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="json-all", type_num=type_num)
        if isinstance(result, dict) and "settings" in result:
            return result["settings"]

    def solr_params(self, query="slub", qtype="default", facet={}, page=0, count=0, sort="", type_num=None):
        url = self.url_query(query=query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="raw-solr-response", type_num=type_num)
        url = utils.add_tx_param(url, "omitHeader", "false")
        result = utils.json_request(url)
        if isinstance(result, dict) and "responseHeader" in result:
            if isinstance(result["responseHeader"], dict) and "params" in result["responseHeader"]:
                return result["responseHeader"]["params"]
