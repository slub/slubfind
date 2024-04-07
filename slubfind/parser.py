from txpyfind.parser import JSONResponse


class AppDetails(JSONResponse):

    def __init__(self, plain):
        self.found = '"id" : ""' not in plain
        super().__init__(plain)
