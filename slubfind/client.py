import re
from txpyfind import utils
from txpyfind.client import Find
from txpyfind.parser import JSONResponse

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
                     "series2",
                     "provenance"
                     ],
                 facets=[
                     "facet_avail",
                     "format_de14",
                     "publishDateSort",
                     "branch_collcode",
                     "branch",
                     "license",
                     "access_state",
                     "language",
                     "thema",
                     "author",
                     "facet_music_notation_de14",
                     "music_heading_browse",
                     "provenance",
                     "mega_collection"
                     ],
                 count_limit=1000,
                 sort_pattern=re.compile(r"^(score|publishDateSort|title_sort|id)[+ ](asc|desc)$"),
                 export_format="app",
                 export_page=1369315142,
                 parser_class=JSONResponse):
        super().__init__(base_url,
                         document_path=document_path,
                         query_types=query_types,
                         facets=facets,
                         count_limit=count_limit,
                         sort_pattern=sort_pattern,
                         export_format=export_format,
                         export_page=export_page,
                         parser_class=parser_class)

    def app_details(self, document_id, type_num=None):
        return self.get_document(document_id, data_format="app", type_num=type_num, parser_class=AppDetails)

    def app_search(self, query, qtype="default", facet={}, page=0, count=0, sort="", type_num=None, parser_class=None):
        return self.get_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="app", type_num=type_num, parser_class=parser_class)

    def settings(self):
        url = self.url_query("qqqqq", qtype="default", facet={}, page=0, count=0, sort="", data_format="json-all", type_num=None)
        response = utils.json_request(url)
        if isinstance(response, dict) and "settings" in response:
            return response["settings"]

    def solr_params(self, query, qtype="default", facet={}, page=0, count=0, sort="", type_num=None):
        url = self.url_query(query=query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="json-solr-params", type_num=type_num)
        url = utils.add_tx_param(url, "omitHeader", "false")
        response = utils.json_request(url)
        if isinstance(response, dict):
            return response

    def solr_request(self, query, qtype="default", facet={}, page=0, count=0, sort="", type_num=None):
        url = self.url_query(query=query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="json-solr-request", type_num=type_num)
        url = utils.add_tx_param(url, "debug", "1")
        response = utils.json_request(url)
        if isinstance(response, dict) and "url" in response:
            return response["url"]
