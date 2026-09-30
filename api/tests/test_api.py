def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["collections"]["public"] > 0
    assert "embedding_model" not in body


def test_public_search(client):
    response = client.post("/api/search", json={"query": "Vidzy analytics", "scope": "public", "limit": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["results"]
    assert all(item["metadata"]["scope"] == "public" for item in body["results"])
    assert all("source_document" not in item["metadata"] for item in body["results"])


def test_internal_search_requires_key(client):
    payload = {"query": "private operational notes", "scope": "internal", "limit": 3}
    assert client.post("/api/search", json=payload).status_code == 403
    response = client.post("/api/search", json=payload, headers={"X-Internal-API-Key": "test-internal-key"})
    assert response.status_code == 200
    assert isinstance(response.json()["results"], list)


def test_chat_returns_canonical_answer(client):
    response = client.post("/api/chat", json={"message": "Can I export captured leads?"})
    assert response.status_code == 200
    body = response.json()
    assert body["response_type"] == "direct_answer"
    assert body["response_mode"] == "retrieval"
    assert "CSV" in body["answer"]


def test_chat_retrieval_details_are_public_safe(client):
    response = client.post("/api/chat", json={"message": "Can I show a CTA while my video is playing?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == (
        "Yes. Vidzy lets you show a CTA at a configured point during video playback, "
        "and the timing can be customized for individual videos."
    )
    assert body["sources"][0]["category"] == "cta"
    detail = body["retrieval_details"][0]
    assert detail["id"] == "faq-timed-cta"
    assert detail["document_type"] == "canonical_question"
    assert set(detail) == {"id", "label", "score", "category", "document_type"}


def test_internal_knowledge_cannot_leak_through_chat(client):
    response = client.post("/api/chat", json={"message": "What private operational notes are available?"})
    assert response.status_code == 200
    assert all(source["document_type"] == "canonical_question" for source in response.json()["sources"])


def test_request_validation_and_safe_error(client):
    response = client.post("/api/chat", json={"message": "x"})
    assert response.status_code == 422
    assert response.json()["error"] == "invalid_request"
    response = client.post("/api/chat", json={"message": "x" * 501})
    assert response.status_code == 422
    assert "traceback" not in response.text.lower()
