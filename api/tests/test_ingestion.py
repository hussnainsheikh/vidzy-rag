from api.app.ingestion.index import index_knowledge


def test_ingestion_builds_separate_collections(indexed_runtime):
    _, manager, _, _, counts = indexed_runtime
    assert counts["public"] > 39
    assert counts["internal"] > 0
    assert manager.count("public") == counts["public"]
    assert manager.count("internal") == counts["internal"]
    assert manager.collection_name("public") != manager.collection_name("internal")


def test_repeated_ingestion_is_idempotent(indexed_runtime):
    settings, manager, _, _, first = indexed_runtime
    second = index_knowledge(settings)
    assert second == first
    assert manager.count("public") == first["public"]
    assert manager.count("internal") == first["internal"]
