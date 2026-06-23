from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def log_existing_results(results_path: Path, experiment_name: str) -> None:
    try:
        import mlflow
    except ImportError as exc:
        raise RuntimeError("MLflow n'est pas installe. Installez requirements.txt ou utilisez Docker.") from exc

    df = pd.read_csv(results_path)
    mlflow.set_experiment(experiment_name)
    for _, row in df.iterrows():
        model_name = str(row.get("modele", results_path.stem))
        with mlflow.start_run(run_name=model_name):
            for column, value in row.items():
                if column == "modele":
                    continue
                try:
                    mlflow.log_metric(column, float(value))
                except (TypeError, ValueError):
                    mlflow.log_param(column, value)
            mlflow.log_artifact(str(results_path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=Path("notebooks/Models/result_xgboost_6modeles.csv"))
    parser.add_argument("--experiment-name", default="compagnon-immo")
    args = parser.parse_args()
    log_existing_results(args.results, args.experiment_name)


if __name__ == "__main__":
    main()

