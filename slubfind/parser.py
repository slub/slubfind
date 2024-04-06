from txpyfind.parser import JSONResponse


class AppDetails(JSONResponse):

    def __init__(self, plain):
        super().__init__(plain)
