from slubfind.client import SlubFind


def test_get_document():
    slub_find = SlubFind()
    result = slub_find.app_document("0-1132486122")
    assert result is not None
    assert isinstance(result.raw, dict)
    assert "id" in result.raw


def test_get_holding_status_document():
    slub_find = SlubFind()
    result = slub_find.holding_status_document("0-1132486122")
    assert result is not None
    assert isinstance(result.raw, dict)


def test_get_query():
    slub_find = SlubFind()
    result = slub_find.app_search("manfred bonitz")
    assert result is not None
    assert isinstance(result.raw, dict)


def test_settings():
    slub_find = SlubFind()
    result = slub_find.settings()
    assert result is not None
    assert isinstance(result, dict)


def test_solr_params():
    slub_find = SlubFind()
    result = slub_find.solr_params("manfred bonitz")
    assert result is not None
    assert isinstance(result, dict)


def test_solr_params_via_url():
    slub_find = SlubFind()
    result = slub_find.solr_params_via_url(
        "https://katalog.slub-dresden.de/"
        "?tx_find_find%5Bq%5D%5Bdefault%5D=manfred+bonitz")
    assert result is not None
    assert isinstance(result, dict)


def test_get_query_raw_solr_response():
    slub_find = SlubFind(export_format="raw-solr-response")
    result = slub_find.get_query("manfred bonitz")
    assert result is not None
    assert isinstance(result.raw, dict)
    assert "response" in result.raw


def test_solr_request():
    slub_find = SlubFind()
    result = slub_find.solr_request("manfred bonitz")
    assert result is not None
    assert isinstance(result, str)
    assert result.startswith("http")
