from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from api.config import COMMUNES_PATH, META_PATH, MODEL_DIR
from api.features import FeatureContext, build_feature_frame
from api.schemas import PredictionRequest


@dataclass
class PredictionResult:
    eur_m2: float
    total_eur: float
    interval_low_eur: float
    interval_high_eur: float
    segment: str
    model_source: str
    features_used: int


class ModelService:
    def __init__(
        self,
        meta_path: Path = META_PATH,
        model_dir: Path = MODEL_DIR,
        communes_path: Path = COMMUNES_PATH,
    ) -> None:
        self.meta_path = meta_path
        self.model_dir = model_dir
        self.communes_path = communes_path
        self.meta: dict = {}
        self.models: dict[str, object] = {}
        self.communes = pd.DataFrame()
        self.loaded = False

    def load(self) -> None:
        with self.meta_path.open("rb") as handle:
            self.meta = pickle.load(handle)

        if self.communes_path.exists():
            self.communes = pd.read_csv(
                self.communes_path,
                dtype={"code_commune": str, "code_departement": str},
                low_memory=False,
            )
            if "code_commune" in self.communes.columns:
                self.communes["code_commune"] = self.communes["code_commune"].astype(str).str.zfill(5)

        for tranche in ("bas", "milieu", "haut"):
            for type_bien in ("maison", "appart"):
                key = f"{tranche}_{type_bien}"
                path = self.model_dir / f"model_xgb_{tranche}_{type_bien}.pkl"
                with path.open("rb") as handle:
                    self.models[key] = pickle.load(handle)
        self.loaded = True

    @property
    def context(self) -> FeatureContext:
        if not self.meta:
            raise RuntimeError("Le service modele n'est pas charge.")
        return FeatureContext(
            features=list(self.meta["features"]),
            q33=float(self.meta["q33"]),
            q66=float(self.meta["q66"]),
            communes=self.communes,
        )

    def predict(self, request: PredictionRequest) -> PredictionResult:
        if not self.loaded:
            self.load()

        frame, segment, fallback_price = build_feature_frame(request, self.context)
        model = self.models[segment]
        eur_m2 = float(model.predict(frame)[0])
        if fallback_price and (eur_m2 < fallback_price * 0.5 or eur_m2 > fallback_price * 2.0):
            eur_m2 = fallback_price
        eur_m2 = max(float(self.meta.get("prix_m2_min", 300)), eur_m2)
        eur_m2 = min(float(self.meta.get("prix_m2_max", 25000)), eur_m2)

        total = eur_m2 * request.surface_reelle_bati
        return PredictionResult(
            eur_m2=eur_m2,
            total_eur=total,
            interval_low_eur=total * 0.85,
            interval_high_eur=total * 1.15,
            segment=segment,
            model_source="xgboost_6_segments",
            features_used=len(frame.columns),
        )
