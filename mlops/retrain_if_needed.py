from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pandas as pd


def should_retrain(metrics_path: Path, max_mape: float) -> bool:
    metrics = pd.read_csv(metrics_path)
    if "mape" not in metrics.columns:
        raise ValueError("La colonne 'mape' est requise pour decider le retraining.")
    return float(metrics["mape"].iloc[-1]) > max_mape


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, default=Path("notebooks/Models/result_xgboost_6modeles.csv"))
    parser.add_argument("--max-mape", type=float, default=32.0)
    parser.add_argument("--command", default="python mlops/train_baseline.py")
    args = parser.parse_args()

    if should_retrain(args.metrics, args.max_mape):
        raise SystemExit(subprocess.call(args.command, shell=True))
    print("Aucun retraining necessaire.")


if __name__ == "__main__":
    main()

