from __future__ import annotations

import time
from contextlib import asynccontextmanager
from os import getenv
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

from api.config import MODEL_DIR
from api.model_service import ModelService
from api.schemas import HealthResponse, PredictionRequest, PredictionResponse

model_service = ModelService()
PREDICTION_COUNT = Counter("immo_predictions_total", "Nombre total de predictions API")
PREDICTION_LATENCY = Histogram("immo_prediction_latency_seconds", "Latence des predictions")
PREDICTION_ERRORS = Counter("immo_prediction_errors_total", "Nombre d'erreurs de prediction")


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        model_service.load()
    except Exception:
        model_service.loaded = False
    yield


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    expected = getenv("IMMO_API_KEY")
    if expected and x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cle API manquante ou invalide.",
        )


app = FastAPI(
    title="Compagnon Immobilier API",
    description="API d'inference pour estimer un prix immobilier au m2.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok" if model_service.loaded else "degraded",
        model_loaded=model_service.loaded,
        communes_loaded=not model_service.communes.empty,
        model_dir=str(MODEL_DIR),
    )


@app.post("/predict", response_model=PredictionResponse, dependencies=[Depends(require_api_key)])
def predict(payload: PredictionRequest) -> PredictionResponse:
    start = time.perf_counter()
    try:
        result = model_service.predict(payload)
    except Exception as exc:
        PREDICTION_ERRORS.inc()
        raise HTTPException(status_code=500, detail=f"Prediction impossible: {exc}") from exc
    finally:
        PREDICTION_LATENCY.observe(time.perf_counter() - start)

    PREDICTION_COUNT.inc()
    return PredictionResponse(
        prediction_eur_m2=round(result.eur_m2, 2),
        prediction_total_eur=round(result.total_eur, 2),
        interval_low_eur=round(result.interval_low_eur, 2),
        interval_high_eur=round(result.interval_high_eur, 2),
        model_segment=result.segment,
        model_source=result.model_source,
        features_used=result.features_used,
    )


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
