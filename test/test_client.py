from slubfind.client import SlubFind

def test_get_document():
    # create SlubFind instance
    slub_find = SlubFind()
    # retrieve JSON data (detail view, app format)
    slub_app_doc = slub_find.app_document("0-1132486122")
    assert slub_app_doc is not None

def test_get_query():
    # create SlubFind instance
    slub_find = SlubFind()
    # retrieve JSON data (query view, app format)
    slub_app_query = slub_find.app_search("manfred bonitz")
    assert slub_app_query is not None

def test_settings():
    # create SlubFind instance
    slub_find = SlubFind()
    # retrieve TYPO3-find settings (query view)
    slub_find_settings = slub_find.settings()
    assert slub_find_settings is not None

#def test_solr_params():
#    # create SlubFind instance
#    slub_find = SlubFind()
#    # retrieve Solr parameters (query view)
#    slub_find_solr_params = slub_find.solr_params("manfred bonitz")
#    assert slub_find_solr_params is not None

#def test_solr_params_via_url():
#    # create SlubFind instance
#    slub_find = SlubFind()
#    # retrieve Solr parameters (query view)
#    slub_find_solr_params_via_url = slub_find.solr_params_via_url("https://katalog.slub-dresden.de/?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz")
#    assert slub_find_solr_params_via_url is not None

def test_solr_request():
    # create SlubFind instance
    slub_find = SlubFind()
    # retrieve Solr URL (query view)
    slub_find_solr_request = slub_find.solr_request("manfred bonitz")
    assert slub_find_solr_request is not None
