"""
Page 9 — Monitoring & Drift Detection
Affiche les métriques Prometheus + rapports Evidently
"""
import os
import json
import subprocess
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Monitoring & Drift — Compagnon Immobilier",
    page_icon="📡",
    layout="wide",
)

# ── Style ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 8px 0;
}
.drift-ok    { border-left: 4px solid #00d4aa; }
.drift-warn  { border-left: 4px solid #ffa500; }
.drift-alert { border-left: 4px solid #ff4b4b; }
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #00d4aa;
    margin: 24px 0 12px 0;
    border-bottom: 1px solid #0f3460;
    padding-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📡 Monitoring & Drift Detection")
st.markdown("**Phase 4 MLOps** — Surveillance du modèle en production via Prometheus, Grafana et Evidently")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔴 Métriques API en direct",
    "📊 Drift des données",
    "🔗 Liens externes",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Métriques Prometheus en direct
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Métriques API — Prometheus</div>', unsafe_allow_html=True)

    API_URL = os.environ.get("API_URL", "http://localhost:8000")
    PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://immo-prometheus:9090")

    def query_prometheus(query: str):
        try:
            r = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": query},
                timeout=5,
            )
            data = r.json()
            if data["status"] == "success" and data["data"]["result"]:
                return float(data["data"]["result"][0]["value"][1])
        except Exception:
            pass
        return None

    def get_api_health():
        try:
            r = requests.get(f"{API_URL}/health", timeout=5)
            return r.json()
        except Exception:
            return None

    col_refresh = st.columns([8, 2])
    with col_refresh[1]:
        if st.button("🔄 Actualiser"):
            st.rerun()

    health = get_api_health()
    total_preds  = query_prometheus("sum(immo_predictions_total)")
    total_errors = query_prometheus("sum(immo_prediction_errors_total)")
    latency_p95  = query_prometheus(
        "histogram_quantile(0.95, sum(rate(immo_prediction_latency_seconds_bucket[5m])) by (le))"
    )
    req_per_min  = query_prometheus("rate(immo_predictions_total[5m]) * 60")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        status = health.get("status", "?") if health else "offline"
        color  = "normal" if status == "ok" else "inverse"
        st.metric("🟢 Statut API", status.upper(), delta=None)

    with c2:
        st.metric(
            "📨 Prédictions totales",
            f"{int(total_preds):,}" if total_preds is not None else "N/A",
        )

    with c3:
        st.metric(
            "❌ Erreurs",
            f"{int(total_errors):,}" if total_errors is not None else "N/A",
        )

    with c4:
        st.metric(
            "⚡ Latence P95",
            f"{latency_p95*1000:.0f} ms" if latency_p95 is not None else "N/A",
        )

    with c5:
        st.metric(
            "📈 Req/min",
            f"{req_per_min:.1f}" if req_per_min is not None else "N/A",
        )

    st.divider()

    # ── Info modèle ───────────────────────────────────────────────────────────
    if health:
        st.markdown('<div class="section-title">Modèle en production</div>', unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.info(f"""
**Modèle** : {health.get('model_name', 'N/A')}
**Version** : {health.get('model_version', 'N/A')}
**Chargé** : {'✅ Oui' if health.get('model_loaded') else '❌ Non'}
""")
        with col_m2:
            try:
                model_info = requests.get(f"{API_URL}/model/info", timeout=5).json()
                metrics = model_info.get("metrics", {})
                st.success(f"""
**R²** : {metrics.get('r2', 'N/A')}
**MAE** : {metrics.get('mae', 'N/A')} €/m²
**RMSE** : {metrics.get('rmse', 'N/A')}
""")
            except Exception:
                st.warning("Métriques modèle indisponibles")
    else:
        st.error("⚠️ API hors ligne — démarrez Docker avec `docker compose up -d`")

    st.divider()

    # ── Architecture monitoring ────────────────────────────────────────────────
    st.markdown('<div class="section-title">Architecture de monitoring</div>', unsafe_allow_html=True)
    st.markdown("""
```
FastAPI /metrics  ──scrape 15s──▶  Prometheus :9090
                                        │
                                   PromQL queries
                                        │
                                        ▼
                                   Grafana :3000
                                  (Dashboards live)
```
""")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
**Métriques exposées :**
- `immo_predictions_total` — compteur cumulatif
- `immo_prediction_errors_total` — erreurs 5xx
- `immo_prediction_latency_seconds` — histogramme latence
""")
    with col_b:
        st.markdown("""
**Alertes configurées :**
- 🔴 API down > 1 min → alerte critique
- 🟡 Taux erreur > 5% → alerte warning
- 🟡 Latence P95 > 2s → alerte warning
""")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Drift des données (Evidently)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Détection de drift — Evidently</div>', unsafe_allow_html=True)

    st.markdown("""
**Principe :** Comparer la distribution des données d'entraînement (2022 = référence)
avec les données de production simulées (2024, 2025).
Si la distribution change → **drift détecté** → retraining déclenché.
""")

    REPORTS_DIR = Path(__file__).parents[2] / "monitoring" / "reports"
    DRIFT_SCRIPT = Path(__file__).parents[2] / "monitoring" / "drift_report.py"
    BASE_DIR     = Path(__file__).parents[2]

    # ── Bouton générer rapport ─────────────────────────────────────────────────
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        run_drift = st.button("🚀 Générer rapport drift", type="primary")

    if run_drift:
        csv_ref = BASE_DIR / "dvf_2022_clean.csv"
        if not csv_ref.exists():
            st.error("❌ Fichier dvf_2022_clean.csv introuvable")
        else:
            with st.spinner("Calcul du drift en cours (Evidently)..."):
                result = subprocess.run(
                    [sys.executable, str(DRIFT_SCRIPT)],
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR),
                )
            if result.returncode == 0:
                st.success("✅ Rapports générés avec succès !")
            else:
                st.error(f"❌ Erreur : {result.stderr[:500]}")

    st.divider()

    # ── Résultats drift ───────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Résultats du drift</div>', unsafe_allow_html=True)

    reports = list(REPORTS_DIR.glob("*.html")) if REPORTS_DIR.exists() else []

    # ── Métriques drift JSON ───────────────────────────────────────────────────
    metrics_file = REPORTS_DIR / "drift_metrics.json"
    if metrics_file.exists():
        import json
        with open(metrics_file) as f:
            drift_metrics = json.load(f)

        st.markdown("**Résumé du drift :**")
        mcols = st.columns(len(drift_metrics))
        for i, (label, m) in enumerate(drift_metrics.items()):
            display_label = label.replace("_vs_", " → ")
            share = m.get("share_of_drifted_columns", 0)
            detected = m.get("drift_detected", False)
            with mcols[i]:
                color = "🔴" if detected else "🟢"
                st.metric(
                    label=f"{color} {display_label}",
                    value=f"{share:.0%} features en drift",
                    delta="Drift détecté !" if detected else "Stable",
                    delta_color="inverse" if detected else "normal",
                )

    if not reports:
        st.info("💡 Cliquez sur **Générer rapport drift** pour lancer l'analyse Evidently.")
    else:
        # Tableau récapitulatif
        drift_data = []
        for r in sorted(reports):
            if r.suffix != ".html":
                continue
            label = r.stem.replace("data_drift_", "").replace("_vs_", " → ")
            drift_data.append({
                "Comparaison": label,
                "Fichier": r.name,
                "Généré": datetime.fromtimestamp(r.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "Taille": f"{r.stat().st_size / 1024:.1f} Ko",
            })

        df_reports = pd.DataFrame(drift_data)
        st.dataframe(df_reports, use_container_width=True, hide_index=True)

        # Affichage des rapports HTML
        st.markdown("**Rapports détaillés :**")
        for r in sorted(reports):
            label = r.stem.replace("data_drift_", "").replace("_vs_", " → ")
            with st.expander(f"📄 Rapport : {label}"):
                with open(r, "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=600, scrolling=True)

    st.divider()

    # ── Explication des types de drift ────────────────────────────────────────
    st.markdown('<div class="section-title">Types de drift détectés</div>', unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("""
**Data Drift** (P(X) change)
- Distribution des features change
- Ex: prix/m² moyen augmente en 2025 vs 2022
- Détecté par : Kolmogorov-Smirnov, PSI

**Concept Drift** (P(Y|X) change)
- Relation feature → target change
- Ex: le modèle prédit moins bien en 2025
- Détecté par : dégradation des métriques
""")
    with col_d2:
        # Graphique simulé de drift
        years = ["2020", "2021", "2022\n(réf.)", "2023", "2024", "2025"]
        prix_m2 = [2800, 3100, 3400, 3600, 3750, 3900]
        colors  = ["#636EFA"] * 2 + ["#00d4aa"] + ["#EF553B"] * 3

        fig = go.Figure(go.Bar(
            x=years,
            y=prix_m2,
            marker_color=colors,
            text=[f"{p:,} €" for p in prix_m2],
            textposition="outside",
        ))
        fig.update_layout(
            title="Prix médian/m² par année (drift temporel)",
            yaxis_title="€/m²",
            height=300,
            margin=dict(t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Pipeline retraining ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Pipeline de retraining automatique</div>', unsafe_allow_html=True)

    st.markdown("""
```
Données prod  ──▶  Evidently  ──▶  Drift > seuil ?
                                        │ OUI
                                        ▼
                               Airflow DAG déclenché
                                        │
                          ┌─────────────┼─────────────┐
                          ▼             ▼              ▼
                     collect_data  preprocess    train_model
                                                      │
                                                      ▼
                                              MLflow Registry
                                             (nouvelle version)
                                                      │
                                                      ▼
                                            API /reload_model
                                         (nouveau modèle actif)
```
""")

    col_air1, col_air2 = st.columns(2)
    with col_air1:
        st.info("""
**DAG Airflow :** `compagnon_immo_pipeline`
- Schedule : @weekly (+ déclenché sur drift)
- Étapes : collect → preprocess → train → reload
- MLflow tracking : http://localhost:5000
""")
    with col_air2:
        st.success("""
**Seuils d'alerte configurés :**
- 🟡 Drift > 30% des features → warning
- 🔴 Drift > 50% des features → retraining auto
- 📊 MAE dégradé > 10% → investigation
""")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Liens externes
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Accès aux outils de monitoring</div>', unsafe_allow_html=True)

    tools = [
        {
            "icon": "📊",
            "name": "Grafana",
            "url": "http://localhost:3000",
            "desc": "Dashboards en temps réel — métriques API, latence, erreurs",
            "creds": "admin / admin",
        },
        {
            "icon": "🔥",
            "name": "Prometheus",
            "url": "http://localhost:9090",
            "desc": "Base de données time-series — requêtes PromQL",
            "creds": "Accès direct",
        },
        {
            "icon": "🌊",
            "name": "MLflow",
            "url": "http://localhost:5000",
            "desc": "Model Registry — versions, métriques, artifacts",
            "creds": "Accès direct",
        },
        {
            "icon": "🌀",
            "name": "Airflow",
            "url": "http://localhost:8080",
            "desc": "Orchestration des pipelines de retraining",
            "creds": "admin / admin",
        },
    ]

    cols = st.columns(2)
    for i, tool in enumerate(tools):
        with cols[i % 2]:
            st.markdown(f"""
**{tool['icon']} {tool['name']}**
- 🔗 [{tool['url']}]({tool['url']})
- {tool['desc']}
- 🔑 `{tool['creds']}`
""")
            st.markdown("---")

    st.markdown('<div class="section-title">Stack technique complète</div>', unsafe_allow_html=True)
    st.markdown("""
| Composant | Rôle | Port |
|-----------|------|------|
| **FastAPI** | API de prédiction + `/metrics` | 8000 |
| **Prometheus** | Collecte métriques (scrape 15s) | 9090 |
| **Grafana** | Visualisation dashboards | 3000 |
| **Evidently** | Détection drift data/concept | — |
| **Airflow** | Orchestration retraining | 8080 |
| **MLflow** | Model Registry + Tracking | 5000 |
| **PostgreSQL** | BDD Airflow | 5432 |
| **Nginx** | Reverse proxy | 80/443 |
| **Streamlit** | Interface utilisateur | 8501 |
""")
