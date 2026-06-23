"""
Cree la structure mlruns/ au format MLflow sans dependance mlflow.
Les runs generes sont lisibles par 'mlflow ui' une fois mlflow installe.

Format MLflow local (backend=file) :
  mlruns/
    <experiment_id>/
      meta.yaml
      <run_id>/
        meta.yaml
        metrics/<metric_name>   (ligne: timestamp value step)
        params/<param_name>     (valeur brute)
        tags/<tag_name>         (valeur brute)
        artifacts/              (vide ou lien)
"""
from __future__ import annotations

import time
import uuid
from pathlib import Path

import pandas as pd

RESULTS_CSV    = Path("notebooks/Models/result_xgboost_6modeles.csv")
MLRUNS_DIR     = Path("mlruns")
EXPERIMENT_ID  = "1"
EXPERIMENT_NAME = "compagnon-immo-xgboost-6segments"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_experiment(exp_dir: Path) -> None:
    meta = (
        f"artifact_location: {exp_dir.resolve().as_posix()}/artifacts\n"
        f"experiment_id: '{EXPERIMENT_ID}'\n"
        f"lifecycle_stage: active\n"
        f"name: {EXPERIMENT_NAME}\n"
    )
    _write(exp_dir / "meta.yaml", meta)


def create_run(exp_dir: Path, row: pd.Series) -> str:
    run_id  = uuid.uuid4().hex
    ts_ms   = int(time.time() * 1000)
    segment = str(row.get("segment", run_id[:8]))
    run_dir = exp_dir / run_id

    # meta.yaml du run
    meta = (
        f"artifact_uri: {(run_dir / 'artifacts').resolve().as_posix()}\n"
        f"end_time: {ts_ms + 100}\n"
        f"entry_point_name: ''\n"
        f"experiment_id: '{EXPERIMENT_ID}'\n"
        f"lifecycle_stage: active\n"
        f"run_id: {run_id}\n"
        f"run_name: {segment}\n"
        f"source_name: mlops/log_to_mlflow_local.py\n"
        f"source_type: 1\n"
        f"source_version: ''\n"
        f"start_time: {ts_ms}\n"
        f"status: 3\n"  # FINISHED
        f"user_id: wided\n"
    )
    _write(run_dir / "meta.yaml", meta)

    # Metriques
    for col in ("r2", "mae", "rmse", "mape", "train_time_sec"):
        if col in row and pd.notna(row[col]):
            _write(run_dir / "metrics" / col, f"{ts_ms} {float(row[col]):.6f} 0\n")

    # Params
    for col in ("n_train",):
        if col in row and pd.notna(row[col]):
            _write(run_dir / "params" / col, str(int(row[col])))

    # Tags
    tags = {
        "mlflow.runName":    segment,
        "mlflow.user":       "wided",
        "mlflow.source.type": "LOCAL",
        "segment":           segment,
        "tranche":           str(row.get("tranche", "")),
        "type_bien":         str(row.get("type", "")),
        "source_csv":        str(RESULTS_CSV),
    }
    for k, v in tags.items():
        _write(run_dir / "tags" / k, v)

    # Dossier artifacts vide (requis par mlflow ui)
    (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)

    return run_id


def main() -> None:
    df = pd.read_csv(RESULTS_CSV)
    print(f"Chargement : {RESULTS_CSV} ({len(df)} lignes)")

    exp_dir = MLRUNS_DIR / EXPERIMENT_ID
    create_experiment(exp_dir)

    # Fichier d'index des experiments requis par mlflow ui
    _write(
        MLRUNS_DIR / "models" / ".trash" / ".gitkeep", ""
    )
    _write(
        MLRUNS_DIR / ".trash" / ".gitkeep", ""
    )

    run_ids = []
    for _, row in df.iterrows():
        run_id = create_run(exp_dir, row)
        run_ids.append(run_id)
        print(f"  Run cree : {row.get('segment')} -> {run_id[:8]}...")

    print(f"\n{len(run_ids)} runs crees dans {MLRUNS_DIR}/")
    print("\nPour visualiser quand mlflow est disponible :")
    print("  mlflow ui --backend-store-uri mlruns --port 5000")
    print("  Puis ouvrir : http://localhost:5000")


if __name__ == "__main__":
    main()
