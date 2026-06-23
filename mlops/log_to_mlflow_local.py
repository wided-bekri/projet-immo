"""
Enregistre les resultats XGBoost existants dans MLflow via backend fichier local.
Ne requiert pas de serveur MLflow. Cree mlruns/ dans le dossier courant.

Usage :
    python mlops/log_to_mlflow_local.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RESULTS_CSV = Path("notebooks/Models/result_xgboost_6modeles.csv")
EXPERIMENT_NAME = "compagnon-immo-xgboost-6segments"
TRACKING_URI = "mlruns"


def main() -> None:
    try:
        import mlflow
    except ModuleNotFoundError:
        print("ERREUR : mlflow n'est pas installe.")
        print("Installez-le avec : pip install mlflow")
        sys.exit(1)

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    df = pd.read_csv(RESULTS_CSV)
    print(f"Chargement : {RESULTS_CSV} ({len(df)} lignes)")
    print(f"Colonnes   : {df.columns.tolist()}")

    logged = 0
    for _, row in df.iterrows():
        segment = str(row.get("segment", f"run_{logged}"))
        with mlflow.start_run(run_name=segment):
            # Tags
            mlflow.set_tag("segment", segment)
            mlflow.set_tag("tranche", str(row.get("tranche", "")))
            mlflow.set_tag("type_bien", str(row.get("type", "")))
            mlflow.set_tag("source", "result_xgboost_6modeles.csv")

            # Metriques
            for col in ("r2", "mae", "rmse", "mape", "train_time_sec"):
                if col in row and pd.notna(row[col]):
                    mlflow.log_metric(col, float(row[col]))

            # Params
            for col in ("n_train",):
                if col in row and pd.notna(row[col]):
                    mlflow.log_param(col, int(row[col]))

            # Artefact : le CSV source
            mlflow.log_artifact(str(RESULTS_CSV))

        logged += 1
        print(f"  Run enregistre : {segment}")

    print(f"\n{logged} runs enregistres dans {TRACKING_URI}/")
    print(f"Pour visualiser : mlflow ui --backend-store-uri {TRACKING_URI} --port 5000")


if __name__ == "__main__":
    main()
