import streamlit as st
import requests
import os

st.set_page_config(page_title="Monitoring & Cycle de vie", layout="wide")

st.title("📈 Monitoring & Cycle de vie")

st.markdown("""
Un modèle ML en production peut se dégrader avec le temps.
Les prix immobiliers changent, le marché évolue.
Cette page montre comment on **surveille** le modèle et comment on le **met à jour automatiquement**.
""")

st.markdown("---")

st.header("1. Prometheus : surveiller l'API")

st.markdown("""
**Prometheus** collecte des métriques sur notre API toutes les **15 secondes**.
Il va automatiquement chercher les données sur `api:8000/metrics` — on appelle ça le "scraping".
""")

st.markdown("**Les 3 métriques qu'on suit :**")

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("**📊 immo_predictions_total**")
        st.markdown("Nombre total de prédictions faites depuis le démarrage. S'incrémente à chaque appel à /predict.")
with col2:
    with st.container(border=True):
        st.markdown("**❌ immo_prediction_errors_total**")
        st.markdown("Nombre d'erreurs. Si ce chiffre monte, il y a un problème avec le modèle ou les données d'entrée.")
with col3:
    with st.container(border=True):
        st.markdown("**⏱️ immo_prediction_latency_seconds**")
        st.markdown("Temps de réponse de chaque prédiction. On surveille notamment le P95 (95% des requêtes).")

# Tentative de récupérer les vraies métriques
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")

try:
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": "immo_predictions_total"}, timeout=3)
    if r.status_code == 200:
        data = r.json()
        results = data.get("data", {}).get("result", [])
        if results:
            total = results[0]["value"][1]
            st.metric("Prédictions totales (temps réel)", total)
        else:
            st.info("Prometheus connecté — aucune prédiction encore effectuée.")
except Exception:
    st.info("💡 Prometheus est visible dans Grafana sur http://localhost:3000")

st.markdown("---")

st.header("2. Grafana : visualiser les métriques")

st.markdown("""
**Grafana** se connecte à Prometheus et affiche les métriques sous forme de graphiques.
On a créé un dashboard qui montre en temps réel :
- Le nombre de prédictions
- Le taux d'erreurs
- La latence des requêtes
""")

st.code("""
FastAPI /metrics ──(scrape toutes les 15s)──▶ Prometheus :9090 ──▶ Grafana :3000
""", language="")

st.markdown("**Accès Grafana :** http://localhost:3000 | identifiant : `admin` / `admin`")

st.markdown("---")

st.header("3. Evidently : détecter le drift")

st.markdown("""
Le **drift** c'est quand les données réelles s'éloignent des données d'entraînement.
Par exemple : si les prix parisiens explosent en 2026, notre modèle entraîné sur 2022
va faire des erreurs de plus en plus grandes.

On utilise **Evidently** pour comparer :
- **Données de référence** : transactions 2022 (ce sur quoi le modèle a été entraîné)
- **Données actuelles** : transactions 2024 et 2025
""")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Seuils d'alerte :**")
    st.markdown("""
    - Drift sur < 30% des variables → **OK**, rien à faire
    - Drift sur 30-50% des variables → **Warning**, surveiller
    - Drift sur > 50% des variables → **Retraining automatique déclenché**
    """)
with col2:
    st.markdown("**Ce qu'Evidently compare :**")
    st.markdown("""
    - La distribution des prix (ont-ils changé ?)
    - La distribution des surfaces
    - La distribution par département
    - etc. pour chacune des 31 variables
    """)

st.markdown("---")

st.header("4. Le cycle de vie complet")

st.markdown("Si le drift est détecté, voici ce qui se passe **automatiquement** :")

st.code("""
Données 2024/2025 (nouvelles)
    ↓
Evidently compare avec données 2022 (référence)
    ↓
Drift > 50% détecté ?
    ↓  OUI
Airflow DAG : drift_monitoring_retraining
    ↓
6 tâches automatiques :
  1. Vérifier le drift
  2. Charger les nouvelles données
  3. Entraîner un nouveau modèle XGBoost
  4. Évaluer les performances
  5. Enregistrer dans MLflow Registry
  6. Recharger l'API avec le nouveau modèle
    ↓
Nouveau modèle en production — sans intervention humaine
""", language="")

st.success("""
✅ **Ce qu'on a mis en place :**
- Surveillance automatique de l'API (Prometheus + Grafana)
- Détection de drift (Evidently)
- Retraining automatique si nécessaire (Airflow)
- Mise à jour du modèle sans toucher au code (MLflow alias "production")
""")
