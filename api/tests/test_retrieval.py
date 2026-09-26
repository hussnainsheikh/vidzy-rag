from api.app.rag import RagService


def test_canonical_question_retrieval(indexed_runtime):
    _, _, retrieval, _, _ = indexed_runtime
    results = retrieval.retrieve(
        "Can Vidzy show calls-to-action during video playback?",
        scope="public",
        limit=3,
        metadata_filter={"document_type": "canonical_question"},
    )
    assert results[0].document.metadata["question_id"] == "faq-timed-cta"


def test_paraphrased_question_retrieval(indexed_runtime):
    _, _, retrieval, _, _ = indexed_runtime
    results = retrieval.retrieve(
        "Will the movie pause when a contact form appears and resume after I submit it?",
        scope="public",
        limit=3,
        metadata_filter={"document_type": "canonical_question"},
    )
    assert "faq-lead-playback" in [item.document.metadata["question_id"] for item in results]


def test_no_answer_behavior(indexed_runtime):
    _, _, _, rag, _ = indexed_runtime
    response = rag.answer("How much flour belongs in sourdough bread?")
    assert response.response_type == "no_reliable_answer"
    assert response.sources == []


def test_retrieval_mode_requires_no_llm_key(indexed_runtime):
    settings, _, retrieval, _, _ = indexed_runtime
    assert settings.openai_api_key is None
    response = RagService(settings, retrieval).answer("Can I export captured leads?")
    assert response.response_mode == "retrieval"
    assert "CSV" in response.answer


def test_generative_mode_falls_back_when_unconfigured(indexed_runtime):
    settings, _, retrieval, _, _ = indexed_runtime
    generative = settings.model_copy(update={"rag_response_mode": "generative", "openai_api_key": None})
    response = RagService(generative, retrieval).answer("Can I export captured leads?")
    assert response.response_type == "direct_answer"
    assert response.response_mode == "retrieval"


def test_public_retrieval_has_no_internal_documents(indexed_runtime):
    _, _, retrieval, _, _ = indexed_runtime
    results = retrieval.retrieve("private operational notes", scope="public", limit=20)
    assert results
    assert all(item.document.metadata["scope"] == "public" for item in results)
