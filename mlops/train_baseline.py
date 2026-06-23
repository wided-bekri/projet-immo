from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def train(input_path: Path, target: str, output_dir: Path) -> dict[str, float]:
    df = pd.read_csv(input_path, low_memory=False)
    if target not in df.columns:
        raise ValueError(f"Colonne cible introuvable: {target}")

    numeric = df.select_dtypes(include=["number"]).drop(columns=[target], errors="ignore")
    y = df[target]
    x_train, x_test, y_train, y_test = train_test_split(numeric.fillna(0), y, test_size=0.2, random_state=42)

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)),
        ]
    )
    pipeline.fit(x_train, y_train)
    preds = pipeline.predict(x_test)

    metrics = {
        "r2": r2_score(y_test, preds),
        "mae": mean_absolute_error(y_test, preds),
        "rmse": mean_squared_error(y_test, preds, squared=False),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(output_dir / "baseline_metrics.csv", index=False)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("dvf_clean_model_ready.csv"))
    parser.add_argument("--target", default="prix_m2")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/baseline"))
    args = parser.parse_args()
    print(train(args.input, args.target, args.output_dir))


if __name__ == "__main__":
    main()

