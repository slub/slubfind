from txpyfind.parser import JSONResponse


class AppDetails(JSONResponse):

    def __init__(self, raw):
        super().__init__(raw)
