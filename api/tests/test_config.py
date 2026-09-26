from api.app.config import Settings


def test_configuration_parsing(monkeypatch, tmp_path):
    monkeypatch.setenv("RAG_RESPONSE_MODE", "generative")
    monkeypatch.setenv("LLM_FALLBACK_TO_RETRIEVAL", "true")
    monkeypatch.setenv("CORS_ORIGINS", "https://rag.example.com,http://localhost:5173")
    settings = Settings(_env_file=None, chroma_path=tmp_path)
    assert settings.rag_response_mode == "generative"
    assert settings.llm_fallback_to_retrieval is True
    assert settings.cors_origins == ["https://rag.example.com", "http://localhost:5173"]


def test_api_keys_do_not_enable_generation(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")
    settings = Settings(_env_file=None, chroma_path=tmp_path)
    assert settings.rag_response_mode == "retrieval"
