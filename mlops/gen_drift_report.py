"""Genere un rapport HTML de derive sans dependance Evidently/Plotly."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


REFERENCE = Path("notebooks/Models/X_train_optimized.csv")
CURRENT   = Path("notebooks/Models/X_test_optimized.csv")
OUTPUT    = Path("monitoring/reports/drift_report.html")
SAMPLE    = 5_000
Z_THRESH  = 0.3


def _analyse(ref: pd.DataFrame, cur: pd.DataFrame) -> list[dict]:
    rows = []
    cols = sorted(set(ref.columns) & set(cur.columns))
    for col in cols:
        r = ref[col].dropna()
        c = cur[col].dropna()
        numeric = pd.api.types.is_numeric_dtype(r)
        r_mean = float(r.mean()) if numeric else None
        c_mean = float(c.mean()) if numeric else None
        r_std  = float(r.std())  if numeric else None
        c_std  = float(c.std())  if numeric else None
        r_null = ref[col].isna().mean() * 100
        c_null = cur[col].isna().mean() * 100
        if r_mean is not None and r_std and r_std > 0:
            z = abs(c_mean - r_mean) / r_std
            drift = z > Z_THRESH
        else:
            z = None
            drift = False
        rows.append({
            "col": col,
            "r_mean": round(r_mean, 2) if r_mean is not None else "cat",
            "c_mean": round(c_mean, 2) if c_mean is not None else "cat",
            "r_std":  round(r_std,  2) if r_std  is not None else "",
            "c_std":  round(c_std,  2) if c_std  is not None else "",
            "r_null": round(r_null, 1),
            "c_null": round(c_null, 1),
            "z":      round(z, 3) if z is not None else "",
            "drift":  drift,
        })
    return rows


def _badge(drifted: int, total: int) -> str:
    ratio = drifted / total if total else 0
    cls = "danger" if ratio > 0.3 else "warn" if drifted > 0 else "ok"
    return f'<span class="badge {cls}">{drifted} / {total}</span>'


def _html(rows: list[dict]) -> str:
    drifted = sum(1 for r in rows if r["drift"])
    total   = len(rows)
    badge   = _badge(drifted, total)

    table_rows = ""
    for r in rows:
        cls  = "drift-yes" if r["drift"] else "drift-no"
        label = "OUI" if r["drift"] else "non"
        table_rows += (
            f'<tr><td>{r["col"]}</td><td>{r["r_mean"]}</td><td>{r["c_mean"]}</td>'
            f'<td>{r["r_std"]}</td><td>{r["c_std"]}</td>'
            f'<td>{r["r_null"]}</td><td>{r["c_null"]}</td>'
            f'<td>{r["z"]}</td><td class="{cls}">{label}</td></tr>\n'
        )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Rapport de Derive - Compagnon Immobilier</title>
<style>
body{{font-family:Arial,sans-serif;margin:30px;background:#f8f9fa}}
h1{{color:#1f4e79}}
h2{{color:#2e75b6;border-bottom:2px solid #2e75b6;padding-bottom:5px}}
.summary{{background:#fff;border-radius:8px;padding:20px;margin:20px 0;box-shadow:0 2px 4px rgba(0,0,0,.1)}}
.badge{{display:inline-block;padding:4px 12px;border-radius:12px;font-weight:bold}}
.ok{{background:#d4edda;color:#155724}}
.warn{{background:#fff3cd;color:#856404}}
.danger{{background:#f8d7da;color:#721c24}}
table{{width:100%;border-collapse:collapse;background:#fff;box-shadow:0 2px 4px rgba(0,0,0,.1);border-radius:8px;overflow:hidden;margin-top:10px}}
th{{background:#2e75b6;color:#fff;padding:10px 12px;text-align:left;font-size:13px}}
td{{padding:8px 12px;border-bottom:1px solid #dee2e6;font-size:12px}}
tr:hover{{background:#f1f8ff}}
.drift-yes{{color:#721c24;font-weight:bold}}
.drift-no{{color:#155724}}
.footer{{color:#999;font-size:11px;margin-top:30px;text-align:center}}
</style>
</head>
<body>
<h1>Rapport de Derive des Donnees</h1>
<p><b>Projet :</b> Compagnon Immobilier &nbsp;|&nbsp;
   <b>Date :</b> 17/06/2026 &nbsp;|&nbsp;
   <b>Methode :</b> Z-score (seuil {Z_THRESH})</p>

<div class="summary">
  <h2>Resume</h2>
  <table style="box-shadow:none">
    <tr>
      <th>Jeu reference</th><td>X_train_optimized.csv ({SAMPLE} lignes)</td>
      <th>Jeu courant</th><td>X_test_optimized.csv ({SAMPLE} lignes)</td>
    </tr>
    <tr>
      <th>Colonnes analysees</th><td>{total}</td>
      <th>Colonnes avec derive</th><td>{badge}</td>
    </tr>
  </table>
  <p style="margin-top:12px;font-size:13px">
    La derive est detectee si |Z-score| &gt; {Z_THRESH},
    c'est-a-dire si la moyenne du jeu courant s'ecarte de plus de {Z_THRESH}
    ecart-type par rapport au jeu de reference.
  </p>
</div>

<h2>Detail par colonne</h2>
<table>
<tr>
  <th>Colonne</th>
  <th>Moyenne ref</th><th>Moyenne courant</th>
  <th>Std ref</th><th>Std courant</th>
  <th>Nulls ref %</th><th>Nulls cur %</th>
  <th>|Z-score|</th><th>Derive ?</th>
</tr>
{table_rows}
</table>

<div class="footer">
  Genere par mlops/gen_drift_report.py &mdash; Compagnon Immobilier 2026
</div>
</body>
</html>"""


def main() -> None:
    print(f"Chargement reference : {REFERENCE}")
    ref = pd.read_csv(REFERENCE, nrows=SAMPLE, low_memory=False)
    print(f"Chargement courant   : {CURRENT}")
    cur = pd.read_csv(CURRENT,   nrows=SAMPLE, low_memory=False)
    print(f"Lignes : ref={len(ref)}, cur={len(cur)}")

    rows = _analyse(ref, cur)
    drifted = sum(1 for r in rows if r["drift"])
    print(f"Colonnes avec derive : {drifted}/{len(rows)}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(_html(rows), encoding="utf-8")
    print(f"Rapport genere : {OUTPUT}")


if __name__ == "__main__":
    main()
