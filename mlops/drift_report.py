from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_drift_report(reference_path: Path, current_path: Path, output_path: Path) -> Path:
    try:
        from evidently.metric_preset import DataDriftPreset
        from evidently.report import Report
    except ImportError as exc:
        raise RuntimeError("Evidently n'est pas installe. Installez requirements.txt ou utilisez Docker.") from exc

    reference = pd.read_csv(reference_path, low_memory=False)
    current = pd.read_csv(current_path, low_memory=False)
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.save_html(str(output_path))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=Path("X_train.csv"))
    parser.add_argument("--current", type=Path, default=Path("X_test.csv"))
    parser.add_argument("--output", type=Path, default=Path("monitoring/reports/drift_report.html"))
    args = parser.parse_args()
    print(build_drift_report(args.reference, args.current, args.output))


if __name__ == "__main__":
    main()

