from txpyfind.parser import JSONResponse


class AppDetails(JSONResponse):

    def __init__(self, plain):
        super().__init__(plain)
        self.found = (isinstance(self.raw, dict) and
                      "id" in self.raw and
                      isinstance(self.raw["id"], str) and
                      len(self.raw["id"].strip()) > 0)
