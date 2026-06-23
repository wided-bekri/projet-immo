import os

from fastapi.testclient import TestClient

from api.main import app, model_service


class DummyModel:
    def predict(self, frame):
        return [2500.0]


PREDICT_PAYLOAD = {
    "surface_reelle_bati": 40,
    "nombre_pieces_principales": 2,
    "type_bien": "appart",
}


def _mock_model_service() -> None:
    model_service.meta = {
        "features": ["surface_reelle_bati", "surface_par_piece", "commune_prix_m2"],
        "q33": 1800,
        "q66": 3100,
        "prix_m2_min": 300,
        "prix_m2_max": 25000,
    }
    model_service.models = {"milieu_appart": DummyModel()}
    model_service.communes = __import__("pandas").DataFrame()
    model_service.loaded = True


# ---------------------------------------------------------------------------
# Tests existants
# ---------------------------------------------------------------------------

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "model_loaded" in response.json()


def test_predict_endpoint_with_mocked_model():
    _mock_model_service()
    client = TestClient(app)
    response = client.post("/predict", json=PREDICT_PAYLOAD)
    assert response.status_code == 200
    payload = response.json()
    assert payload["prediction_eur_m2"] == 2500.0
    assert payload["prediction_total_eur"] == 100000.0
    assert payload["model_segment"] == "milieu_appart"


# ---------------------------------------------------------------------------
# Tests securisation API key
# ---------------------------------------------------------------------------

def test_predict_no_api_key_env_no_header():
    """Sans IMMO_API_KEY definie, /predict fonctionne sans header."""
    os.environ.pop("IMMO_API_KEY", None)
    _mock_model_service()
    client = TestClient(app)
    response = client.post("/predict", json=PREDICT_PAYLOAD)
    assert response.status_code == 200


def test_predict_with_api_key_env_missing_header():
    """Avec IMMO_API_KEY definie, /predict retourne 401 sans header X-API-Key."""
    os.environ["IMMO_API_KEY"] = "secret123"
    _mock_model_service()
    client = TestClient(app)
    response = client.post("/predict", json=PREDICT_PAYLOAD)
    assert response.status_code == 401
    os.environ.pop("IMMO_API_KEY")


def test_predict_with_api_key_env_correct_header():
    """Avec IMMO_API_KEY definie et le bon header, /predict fonctionne."""
    os.environ["IMMO_API_KEY"] = "secret123"
    _mock_model_service()
    client = TestClient(app)
    response = client.post(
        "/predict",
        json=PREDICT_PAYLOAD,
        headers={"X-API-Key": "secret123"},
    )
    assert response.status_code == 200
    os.environ.pop("IMMO_API_KEY")


def test_health_accessible_without_api_key():
    """/health reste accessible sans cle, meme si IMMO_API_KEY est definie."""
    os.environ["IMMO_API_KEY"] = "secret123"
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    os.environ.pop("IMMO_API_KEY")


def test_metrics_accessible_without_api_key():
    """/metrics reste accessible sans cle, meme si IMMO_API_KEY est definie."""
    os.environ["IMMO_API_KEY"] = "secret123"
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    os.environ.pop("IMMO_API_KEY")

