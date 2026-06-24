import os
import pickle
import logging
from contextlib import asynccontextmanager
from typing import Optional

import mlflow
import mlflow.xgboost
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field, field_validator
from prometheus_client import Counter, Histogram, make_asgi_app

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Configuration ===
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MODEL_NAME = "compagnon-immobilier"
META_PATH = os.environ.get(
    "META_PATH",
    os.path.join(os.path.dirname(__file__), "../../../notebooks/Models/meta_6modeles.pkl"),
)
COMMUNES_PATH = os.environ.get(
    "COMMUNES_PATH",
    os.path.join(os.path.dirname(__file__), "../../../app/data/streamlit/communes_streamlit.csv"),
)
IMMO_API_KEY = os.environ.get("IMMO_API_KEY", "")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# === Métriques Prometheus ===
PREDICTION_COUNT = Counter("immo_predictions_total", "Nombre total de prédictions")
PREDICTION_LATENCY = Histogram("immo_prediction_latency_seconds", "Latence des prédictions")
PREDICTION_ERRORS = Counter("immo_prediction_errors_total", "Nombre d'erreurs de prédiction")

# === État global ===
state = {
    "models": {},        # segment -> modèle XGBoost
    "meta": None,        # dict avec q33, q66, features
    "communes": None,    # DataFrame des communes
    "model_version": None,
    "model_loaded": False,
}


# === Schemas ===
class PredictionRequest(BaseModel):
    surface_reelle_bati: float = Field(..., gt=0, le=1000)
    nombre_pieces_principales: int = Field(3, ge=1, le=30)
    type_bien: str = Field("appart")
    code_commune: Optional[str] = Field(None, max_length=5)
    code_departement: Optional[str] = Field(None, max_length=3)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    surface_terrain: float = Field(0.0, ge=0)
    annee: int = Field(2025, ge=2020, le=2035)
    mois: int = Field(6, ge=1, le=12)
    target_dpe_num: int = Field(4, ge=1, le=7)
    cout_total_5_usages: float = Field(0.0, ge=0)
    age_construction: float = Field(30.0, ge=0)

    @field_validator("type_bien")
    @classmethod
    def normalize_type(cls, v: str) -> str:
        v = v.lower().strip()
        if v in ("appartement", "appart"):
            return "appart"
        if v in ("maison",):
            return "maison"
        raise ValueError("type_bien doit être 'appart' ou 'maison'")


class PredictionResponse(BaseModel):
    prediction_eur_m2: float
    prediction_total_eur: float
    interval_low_eur: float
    interval_high_eur: float
    model_segment: str
    model_version: Optional[str]
    features_used: int


# === Chargement du modèle depuis MLflow ===
def load_model_from_mlflow() -> bool:
    client = mlflow.tracking.MlflowClient()

    # Tentative 1 : alias "production"
    try:
        model_version = client.get_model_version_by_alias(MODEL_NAME, "production")
        run_id = model_version.run_id
        meta_path = META_PATH

        # Charger les 6 modèles depuis les artefacts du run
        segments = ["bas_appart", "bas_maison", "milieu_appart", "milieu_maison", "haut_appart", "haut_maison"]
        models = {}
        for seg in segments:
            uri = f"runs:/{run_id}/models/{seg}"
            try:
                models[seg] = mlflow.xgboost.load_model(uri)
                logger.info(f"Modèle chargé depuis MLflow : {seg}")
            except Exception as e:
                logger.warning(f"Modèle {seg} non trouvé dans MLflow : {e}")

        if models:
            state["models"] = models
            state["model_version"] = f"v{model_version.version}"
            state["model_loaded"] = True
            logger.info(f"✅ {len(models)} modèles chargés depuis MLflow registry (v{model_version.version})")
            return True

    except mlflow.exceptions.MlflowException:
        logger.warning("Aucun modèle 'production' dans le registry MLflow — fallback sur .pkl")

    # Tentative 2 : fallback sur les fichiers .pkl locaux
    try:
        models_dir = os.path.join(os.path.dirname(__file__), "../../../notebooks/Models")
        segments = ["bas_appart", "bas_maison", "milieu_appart", "milieu_maison", "haut_appart", "haut_maison"]
        models = {}
        for seg in segments:
            pkl_path = os.path.join(models_dir, f"model_xgb_{seg}.pkl")
            if os.path.exists(pkl_path):
                with open(pkl_path, "rb") as f:
                    models[seg] = pickle.load(f)
                logger.info(f"Modèle chargé depuis .pkl : {seg}")

        if models:
            state["models"] = models
            state["model_version"] = "pkl_local"
            state["model_loaded"] = True
            logger.info(f"✅ {len(models)} modèles chargés depuis fichiers .pkl locaux")
            return True

    except Exception as e:
        logger.error(f"Erreur chargement .pkl : {e}")

    return False


def load_meta() -> bool:
    try:
        with open(META_PATH, "rb") as f:
            state["meta"] = pickle.load(f)
        logger.info(f"Meta chargé : q33={state['meta']['q33']}, q66={state['meta']['q66']}")
        return True
    except Exception as e:
        logger.error(f"Erreur chargement meta : {e}")
        return False


def load_communes() -> bool:
    try:
        state["communes"] = pd.read_csv(COMMUNES_PATH, dtype={"code_commune": str}, low_memory=False)
        logger.info(f"Communes chargées : {len(state['communes'])} lignes")
        return True
    except Exception as e:
        logger.warning(f"CSV communes non trouvé : {e}")
        return False


# === Logique métier ===
def get_tranche(prix_m2: float, q33: float, q66: float) -> str:
    if prix_m2 < q33:
        return "bas"
    if prix_m2 <= q66:
        return "milieu"
    return "haut"


def build_features(req: PredictionRequest) -> tuple[pd.DataFrame, str]:
    meta = state["meta"]
    features_list = meta["features"]
    q33, q66 = meta["q33"], meta["q66"]

    # Valeurs de base depuis la requête
    row = {
        "surface_reelle_bati": req.surface_reelle_bati,
        "nombre_pieces_principales": req.nombre_pieces_principales,
        "surface_terrain": req.surface_terrain,
        "annee": req.annee,
        "mois": req.mois,
        "target_dpe_num": req.target_dpe_num,
        "cout_total_5_usages": req.cout_total_5_usages,
        "age_construction": req.age_construction,
        "surface_par_piece": req.surface_reelle_bati / max(req.nombre_pieces_principales, 1),
    }

    # Code département numérique
    if req.code_departement:
        try:
            row["code_departement"] = int(req.code_departement.replace("A", "0").replace("B", "0"))
        except Exception:
            row["code_departement"] = 0

    # Coordonnées GPS
    if req.latitude:
        row["latitude"] = req.latitude
    if req.longitude:
        row["longitude"] = req.longitude

    # Enrichissement depuis le CSV communes
    fallback_prix = (q33 + q66) / 2  # prix médian pour le routing
    communes_df = state.get("communes")
    if communes_df is not None and req.code_commune:
        match = communes_df[communes_df["code_commune"].astype(str) == str(req.code_commune)]
        if not match.empty:
            commune_row = match.iloc[0]
            for col in communes_df.columns:
                if col not in row and col in features_list:
                    val = commune_row.get(col)
                    if pd.notna(val):
                        row[col] = val
            if "prix_m2_median" in commune_row:
                fallback_prix = float(commune_row["prix_m2_median"])
            elif "prix_moyen" in commune_row:
                fallback_prix = float(commune_row["prix_moyen"])

    # Construire le vecteur complet dans l'ordre exact des features
    feature_row = {}
    for feat in features_list:
        if feat in row:
            feature_row[feat] = row[feat]
        elif communes_df is not None:
            # Utiliser la médiane de la colonne si disponible
            if feat in communes_df.columns:
                feature_row[feat] = float(communes_df[feat].median())
            else:
                feature_row[feat] = 0.0
        else:
            feature_row[feat] = 0.0

    X = pd.DataFrame([feature_row])

    # Déterminer le segment
    tranche = get_tranche(fallback_prix, q33, q66)
    segment = f"{tranche}_{req.type_bien}"

    return X, segment


# === Lifespan ===
@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Démarrage de l'API Compagnon Immobilier...")
    load_meta()
    load_communes()
    load_model_from_mlflow()
    yield
    logger.info("Arrêt de l'API.")


# === Application FastAPI ===
app = FastAPI(
    title="Compagnon Immobilier — API de Prédiction",
    description="Prédit le prix au m² d'un bien immobilier via 6 modèles XGBoost segmentés.",
    version="2.0.0",
    lifespan=lifespan,
)

# Endpoint Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# === Sécurité ===
def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if IMMO_API_KEY and x_api_key != IMMO_API_KEY:
        raise HTTPException(status_code=401, detail="Clé API manquante ou invalide.")


# === Routes ===
@app.get("/health")
def health():
    return {
        "status": "ok" if state["model_loaded"] else "degraded",
        "model_loaded": state["model_loaded"],
        "communes_loaded": state["communes"] is not None,
        "meta_loaded": state["meta"] is not None,
        "model_version": state["model_version"],
        "model_name": MODEL_NAME,
        "n_segments": len(state["models"]),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)

    if not state["model_loaded"]:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=503, detail="Modèles non disponibles. Lancez d'abord l'entraînement.")

    import time
    start = time.time()

    try:
        X, segment = build_features(req)

        if segment not in state["models"]:
            # Fallback sur le segment le plus proche
            available = list(state["models"].keys())
            type_bien = req.type_bien
            candidates = [s for s in available if s.endswith(type_bien)]
            segment = candidates[0] if candidates else available[0]
            logger.warning(f"Segment non trouvé, fallback sur : {segment}")

        model = state["models"][segment]
        prix_m2 = float(model.predict(X)[0])
        prix_m2 = max(state["meta"]["prix_m2_min"], min(state["meta"]["prix_m2_max"], prix_m2))

        prix_total = prix_m2 * req.surface_reelle_bati

        PREDICTION_COUNT.inc()
        PREDICTION_LATENCY.observe(time.time() - start)

        return PredictionResponse(
            prediction_eur_m2=round(prix_m2, 2),
            prediction_total_eur=round(prix_total, 2),
            interval_low_eur=round(prix_total * 0.85, 2),
            interval_high_eur=round(prix_total * 1.15, 2),
            model_segment=segment,
            model_version=state["model_version"],
            features_used=len(state["meta"]["features"]),
        )

    except Exception as e:
        PREDICTION_ERRORS.inc()
        logger.error(f"Erreur prédiction : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {str(e)}")


@app.get("/model/info")
def model_info():
    client = mlflow.tracking.MlflowClient()
    try:
        model_version = client.get_model_version_by_alias(MODEL_NAME, "production")
        run = client.get_run(model_version.run_id)
        return {
            "model_name": MODEL_NAME,
            "production_version": model_version.version,
            "run_id": model_version.run_id,
            "description": model_version.description,
            "metrics": {
                "mae_global": run.data.metrics.get("mae_global"),
                "r2_global": run.data.metrics.get("r2_global"),
                "n_segments": run.data.metrics.get("n_segments_trained"),
            },
            "params": {
                "q33": run.data.params.get("q33"),
                "q66": run.data.params.get("q66"),
                "n_features": run.data.params.get("n_features"),
            },
        }
    except mlflow.exceptions.MlflowException as e:
        return {
            "model_name": MODEL_NAME,
            "production_version": None,
            "info": "Aucun modèle en production dans le registry.",
            "fallback": "Modèles .pkl locaux utilisés.",
        }
