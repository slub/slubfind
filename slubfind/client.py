import re
from txpyfind.client import Find

from .parser import AppDetails


class SlubFind(Find):

    def __init__(self,
                 base_url="https://katalog.slub-dresden.de",
                 document_path="id",
                 query_types=["default", "title", "author"],
                 facets={},
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

    def app_details(self, document_id):
        return self.get_document(document_id, data_format="app", parser_class=AppDetails)

    def app_search(self, query, qtype="default", facet={}, page=0, count=0, sort=""):
        return self.get_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="app")

    def settings(self, query="qqqqq", qtype="default", facet={}, page=0, count=0, sort=""):
        result = self.get_query(query, qtype=qtype, facet=facet, page=page, count=count, sort=sort, data_format="json-all")
        if isinstance(result, dict) and "settings" in result:
            return result["settings"]
