import streamlit as st
import requests
import os

st.set_page_config(page_title="Monitoring & Cycle de vie", layout="wide")

st.title("📈 Monitoring & Cycle de vie")

st.markdown("""
Un modèle en production peut se dégrader avec le temps : les prix changent, le marché évolue.
Cette page montre comment on **surveille l'API** en temps réel et comment le modèle
se **met à jour automatiquement** si les données dérivent.
""")

st.success("""
✅ **Ce qu'on a mis en place :**
- Prometheus collecte les métriques de l'API toutes les 15 secondes
- Grafana affiche ces métriques sous forme de graphiques
- Evidently détecte le drift des données automatiquement
- Airflow relance un retraining si le drift dépasse 30% des variables
""")

st.markdown("---")

# ─── Section 1 : Prometheus ───────────────────────────────────────────────────
st.header("1. Prometheus : surveiller l'API")

st.markdown("""
**Prometheus** va chercher les métriques sur `api:8000/metrics` toutes les **15 secondes**
(c'est ce qu'on appelle le "scraping").
On suit **3 métriques** pour savoir si tout va bien :
""")

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("**📊 Prédictions totales**")
        st.markdown("`immo_predictions_total`")
        st.markdown("Compte le nombre d'appels à `/predict` depuis le démarrage.")
with col2:
    with st.container(border=True):
        st.markdown("**❌ Erreurs totales**")
        st.markdown("`immo_prediction_errors_total`")
        st.markdown("Si ce chiffre monte, quelque chose ne va pas dans le modèle.")
with col3:
    with st.container(border=True):
        st.markdown("**⏱️ Latence**")
        st.markdown("`immo_prediction_latency_seconds`")
        st.markdown("Temps de réponse de chaque prédiction. On surveille le P95.")

try:
    st.image("app/images/prometheus_query.png", caption="Prometheus — requête immo_predictions_total en temps réel", use_container_width=True)
except FileNotFoundError:
    st.warning("prometheus_query.png introuvable.")

# Valeur temps réel si Prometheus accessible
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
try:
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": "immo_predictions_total"}, timeout=3)
    if r.status_code == 200:
        results = r.json().get("data", {}).get("result", [])
        if results:
            st.metric("Prédictions totales (temps réel)", results[0]["value"][1])
except Exception:
    pass

st.markdown("**Accès Prometheus :** [http://localhost:9090](http://localhost:9090)")

st.markdown("---")

# ─── Section 2 : Grafana ──────────────────────────────────────────────────────
st.header("2. Grafana : visualiser les métriques")

st.markdown("""
**Grafana** se connecte à Prometheus et affiche les métriques sous forme de graphiques.
On a créé un dashboard dans le dossier **MLOps → "Compagnon Immobilier - API Monitoring"**
qui montre en temps réel :
- Le nombre de prédictions
- Le taux d'erreurs
- La latence (p50, p95, p99)
""")

st.info("💡 **Phase 2 :** En production réelle, on ajouterait des **alertes automatiques** (ex : alerte si taux d'erreur > 5% ou latence p95 > 2s). Pour cette phase, le dashboard de visualisation est en place.")

try:
    st.image("app/images/grafana_dashboard.png", caption="Dashboard Grafana — Compagnon Immobilier API Monitoring", use_container_width=True)
except FileNotFoundError:
    st.warning("grafana_dashboard.png introuvable.")

st.markdown("**Accès Grafana :** [http://localhost:3000](http://localhost:3000) *(admin / admin)*")

st.markdown("---")

# ─── Section 3 : Evidently ────────────────────────────────────────────────────
st.header("3. Evidently : détecter le drift")

st.markdown("""
Le **drift** c'est quand les nouvelles données s'éloignent des données d'entraînement.
Par exemple : si les prix parisiens explosent en 2026, notre modèle entraîné sur 2022
va faire des erreurs de plus en plus grandes.

**Evidently** compare automatiquement :
- **Référence** : transactions 2022 (données d'entraînement)
- **Actuelles** : transactions 2024 et 2025
""")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("**Seuil de déclenchement :**")
        st.markdown("""
- Drift < 30% des variables → ✅ OK, rien à faire
- Drift **> 30%** des variables → 🔴 **Retraining automatique déclenché**

`DRIFT_THRESHOLD = 0.3` dans le code Airflow
        """)
with col2:
    with st.container(border=True):
        st.markdown("**Ce qu'Evidently analyse :**")
        st.markdown("""
- Distribution des prix
- Distribution des surfaces
- Distribution par département
- Les 31 variables du modèle
        """)

try:
    st.image("app/images/evidently.png", caption="Rapport Evidently — détection du drift sur les données 2022 vs 2024/2025", use_container_width=True)
except FileNotFoundError:
    st.info("Image evidently.png non disponible.")

col_a, col_b = st.columns(2)
path_2024 = "monitoring/reports/data_drift_2022_vs_2024.html"
if os.path.exists(path_2024):
    with open(path_2024, "rb") as f:
        col_a.download_button("📥 Rapport Drift 2022 vs 2024", data=f, file_name="data_drift_2022_vs_2024.html", mime="text/html")
else:
    col_a.warning("Rapport 2024 non trouvé.")

path_2025 = "monitoring/reports/data_drift_2022_vs_2025.html"
if os.path.exists(path_2025):
    with open(path_2025, "rb") as f:
        col_b.download_button("📥 Rapport Drift 2022 vs 2025", data=f, file_name="data_drift_2022_vs_2025.html", mime="text/html")
else:
    col_b.warning("Rapport 2025 non trouvé.")

st.markdown("---")

# ─── Section 4 : Cycle de vie ─────────────────────────────────────────────────
st.header("4. Le cycle de vie automatique")

st.markdown("Si le drift dépasse **30%** des variables, voici ce qui se passe **sans intervention humaine** :")

st.code("""
Nouvelles données (2024 / 2025)
    ↓
Evidently compare avec les données 2022
    ↓
Drift > 30% détecté ?
    ↓ OUI
Airflow déclenche le DAG drift_monitoring_retraining
    ↓
5 tâches automatiques :
  1. check_drift          → lit drift_metrics.json, confirme le drift
  2. decide_retraining    → décide si retraining nécessaire (BranchPythonOperator)
  3. retrain_model        → entraîne un nouveau XGBoost, logue dans MLflow
  4. promote_model        → change l'alias "production" dans le Model Registry
  5. reload_api           → POST /reload_model → l'API charge le nouveau modèle
    ↓
Nouveau modèle en production — sans toucher au code
""", language="")

st.markdown("**Preuve que ça fonctionne — nos 2 DAGs en action :**")

col1, col2 = st.columns(2)
with col1:
    try:
        st.image("app/images/airflow_drift_dag.png", caption="DAG drift_monitoring_retraining — 5 tâches (retraining automatique si drift > 30%)", use_container_width=True)
    except FileNotFoundError:
        st.warning("airflow_drift_dag.png introuvable.")

with col2:
    try:
        st.image("app/images/airflow_dag_detail.png", caption="DAG compagnon_immo_pipeline — 4 tâches (retraining hebdomadaire)", use_container_width=True)
    except FileNotFoundError:
        st.warning("airflow_dag_detail.png introuvable.")

st.markdown("**Accès Airflow :** [http://localhost:8080](http://localhost:8080) *(admin / admin)*")

st.markdown("---")

# ─── Conclusion ───────────────────────────────────────────────────────────────
st.header("🏁 Bilan : un système autonome")

st.success("""
En combinant **Prometheus + Grafana + Evidently + Airflow**, on a un système qui :
- **se surveille** tout seul (métriques temps réel)
- **se corrige** tout seul (retraining si drift)
- **se met à jour** sans intervention (MLflow alias "production")
""")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("**Bénéfices techniques :**")
        st.markdown("""
- Le modèle ne vieillit pas — il s'adapte aux nouvelles données
- Chaque décision est tracée dans MLflow et Airflow
- L'architecture microservices permet des mises à jour sans coupure
        """)
with col2:
    with st.container(border=True):
        st.markdown("**Bénéfices métier :**")
        st.markdown("""
- Les prédictions restent fiables dans le temps
- Aucune intervention manuelle répétitive
- Le système est prêt à passer à l'échelle (Kubernetes)
        """)
