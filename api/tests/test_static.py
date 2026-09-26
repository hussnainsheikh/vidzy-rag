from fastapi.testclient import TestClient

from api.app.config import Settings
from api.app.main import create_app


def test_compiled_frontend_can_be_served(tmp_path):
    static = tmp_path / "dist"
    static.mkdir()
    (static / "index.html").write_text("<main>Vidzy frontend</main>", encoding="utf-8")
    app = create_app(Settings(_env_file=None, app_env="test", static_dir=static, chroma_path=tmp_path / "chroma"))
    with TestClient(app) as client:
        response = client.get("/some/client/route")
    assert response.status_code == 200
    assert "Vidzy frontend" in response.text
