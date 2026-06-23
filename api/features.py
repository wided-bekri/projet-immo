from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from api.schemas import PredictionRequest


DEPT_TO_FLOAT = {"2A": 201.0, "2B": 202.0}


@dataclass(frozen=True)
class FeatureContext:
    features: list[str]
    q33: float
    q66: float
    communes: pd.DataFrame


def dept_to_float(code: str | None) -> float:
    if not code:
        return 0.0
    normalized = str(code).strip().upper().zfill(2)
    if normalized in DEPT_TO_FLOAT:
        return DEPT_TO_FLOAT[normalized]
    try:
        return float(int(normalized))
    except ValueError:
        return 0.0


def get_tranche(prix_m2: float, q33: float, q66: float) -> str:
    if prix_m2 < q33:
        return "bas"
    if prix_m2 <= q66:
        return "milieu"
    return "haut"


def _safe_number(value: object, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _commune_row(communes: pd.DataFrame, code_commune: str | None) -> pd.Series | None:
    if not code_commune or communes.empty or "code_commune" not in communes.columns:
        return None
    code = str(code_commune).zfill(5)
    matched = communes[communes["code_commune"].astype(str).str.zfill(5) == code]
    if matched.empty:
        return None
    return matched.iloc[0]


def _column_default(communes: pd.DataFrame, feature: str) -> float:
    numeric = pd.to_numeric(communes[feature], errors="coerce")
    return _safe_number(numeric.median())


def build_feature_frame(request: PredictionRequest, context: FeatureContext) -> tuple[pd.DataFrame, str, float]:
    row = _commune_row(context.communes, request.code_commune)
    values: dict[str, float] = {}

    for feature in context.features:
        if row is not None and feature in row.index:
            values[feature] = _safe_number(row[feature])
        elif not context.communes.empty and feature in context.communes.columns:
            values[feature] = _column_default(context.communes, feature)
        else:
            values[feature] = 0.0

    values.update(
        {
            "surface_reelle_bati": request.surface_reelle_bati,
            "nombre_pieces_principales": float(request.nombre_pieces_principales),
            "surface_terrain": request.surface_terrain,
            "annee": float(request.annee),
            "mois": float(request.mois),
            "target_dpe_num": float(request.target_dpe_num),
            "cout_total_5_usages": request.cout_total_5_usages,
            "age_construction": request.age_construction,
            "surface_par_piece": request.surface_reelle_bati / max(request.nombre_pieces_principales, 1),
            "has_cout_usages": 1.0 if request.cout_total_5_usages > 0 else 0.0,
            "has_dpe": 1.0,
        }
    )

    if request.latitude is not None:
        values["latitude"] = request.latitude
    if request.longitude is not None:
        values["longitude"] = request.longitude
    if request.code_departement:
        values["code_departement"] = dept_to_float(request.code_departement)

    commune_prix = values.get("commune_prix_m2", 0.0)
    if request.type_bien == "maison":
        typed_price = values.get("commune_prix_m2_maison", 0.0) or values.get("dept_prix_m2_maison", 0.0)
    else:
        typed_price = values.get("commune_prix_m2_appart", 0.0) or values.get("dept_prix_m2_appart", 0.0)

    if not typed_price:
        typed_price = commune_prix or values.get("dept_prix_m2", 0.0)
    values["prix_estime_commune"] = typed_price * request.surface_reelle_bati

    fallback_price = typed_price or commune_prix or context.q33
    segment = f"{get_tranche(fallback_price, context.q33, context.q66)}_{request.type_bien}"

    frame = pd.DataFrame([{feature: values.get(feature, 0.0) for feature in context.features}])
    frame = frame.replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return frame, segment, float(fallback_price)
