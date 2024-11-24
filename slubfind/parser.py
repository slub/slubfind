"""
parser module of ``slubfind``
"""
from txpyfind.parser import JSONResponse


class AppDetails(JSONResponse):
    """
    ``AppDetails`` class from ``slubfind.parser`` module
    """

    def __init__(self, plain):
        super().__init__(plain)
        self.ok = isinstance(self.raw, dict) and "id" in self.raw
        self.found = self.ok and isinstance(
            self.raw["id"], str) and len(self.raw["id"].strip()) > 0
