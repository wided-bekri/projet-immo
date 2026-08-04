"""
Phase 4 - Drift Monitoring avec Evidently 0.7+
Référence : données 2022
Courant    : données 2024 ou 2025
Métriques Prometheus : sauvegardées dans monitoring/reports/drift_metrics.json
"""
import os
import json
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

# ── Colonnes utilisées ────────────────────────────────────────────────────────
NUM_FEATURES = [
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "surface_terrain",
    "longitude",
    "latitude",
    "mois",
]
CAT_FEATURES = [
    "type_local",
    "nature_mutation",
    "code_departement",
]
TARGET = "prix_m2"
ALL_FEATURES = NUM_FEATURES + CAT_FEATURES
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def load_and_prepare(path: str, sample: int = 5000) -> pd.DataFrame:
    # Lecture par chunks pour éviter les OOM sur petits conteneurs
    chunks = []
    for chunk in pd.read_csv(path, low_memory=False, chunksize=10000):
        cols = [c for c in ALL_FEATURES + [TARGET] if c in chunk.columns]
        chunk = chunk[cols].dropna(subset=[TARGET])
        chunk["code_departement"] = chunk["code_departement"].astype(str)
        chunks.append(chunk)
        if sum(len(c) for c in chunks) >= sample:
            break
    df = pd.concat(chunks, ignore_index=True)
    if len(df) > sample:
        df = df.sample(sample, random_state=42)
    return df


METRICS_FILE = os.path.join(REPORTS_DIR, "drift_metrics.json")


def run_data_drift_report(reference: pd.DataFrame, current: pd.DataFrame, label: str):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    report = Report([DataDriftPreset()])
    result = report.run(reference_data=reference, current_data=current)

    out = os.path.join(REPORTS_DIR, f"data_drift_{label}.html")
    result.save_html(out)
    print(f"[drift] Rapport sauvegardé : {out}")

    # Extraire métriques de drift
    share_drifted = 0.0
    drift_detected = False
    try:
        result_dict = result.dict()
        drift_info = result_dict["metrics"][0]["value"]
        share_drifted = drift_info.get("share_of_drifted_columns", 0.0)
        drift_detected = drift_info.get("dataset_drift", share_drifted > 0.3)
        print(f"[drift] 2022 → {label.split('_')[-1]} : drift={drift_detected} ({share_drifted:.1%} features)")
    except Exception:
        print(f"[drift] Rapport {label} généré (extraction métriques échouée).")

    # Sauvegarder métriques JSON pour Prometheus/Streamlit
    metrics = _load_metrics()
    metrics[label] = {
        "drift_detected": bool(drift_detected),
        "share_of_drifted_columns": float(share_drifted),
        "timestamp": pd.Timestamp.now().isoformat(),
    }
    _save_metrics(metrics)

    return result, share_drifted, drift_detected


def _load_metrics() -> dict:
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_metrics(metrics: dict):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[drift] Métriques sauvegardées : {METRICS_FILE}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(__file__))

    print("=== Chargement des données ===")
    ref = load_and_prepare(os.path.join(base, "dvf_2022_clean.csv"))
    cur_2024 = load_and_prepare(os.path.join(base, "dvf_2024_clean.csv"))
    cur_2025 = load_and_prepare(os.path.join(base, "dvf_2025_clean.csv"))

    print(f"Référence 2022 : {len(ref)} lignes")
    print(f"Courant  2024  : {len(cur_2024)} lignes")
    print(f"Courant  2025  : {len(cur_2025)} lignes")

    print("\n=== Rapport drift 2022 -> 2024 ===")
    _, share_2024, detected_2024 = run_data_drift_report(ref, cur_2024, "2022_vs_2024")
    print(f"  → {share_2024:.1%} features en drift | drift global = {detected_2024}")

    print("\n=== Rapport drift 2022 -> 2025 ===")
    _, share_2025, detected_2025 = run_data_drift_report(ref, cur_2025, "2022_vs_2025")
    print(f"  → {share_2025:.1%} features en drift | drift global = {detected_2025}")

    print("\nPhase 4 terminee. Rapports dans monitoring/reports/")
    print("Métriques JSON sauvegardées dans monitoring/reports/drift_metrics.json")
