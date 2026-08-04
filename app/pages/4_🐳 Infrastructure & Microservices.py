import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Infrastructure", layout="wide")

st.title("🐳 Infrastructure & Microservices")

st.markdown("""
**Le problème qu'on avait :** comment faire tourner le projet de la même façon sur ma machine,
sur la machine de Carine, et demain sur un serveur ?

**La solution :** Docker. On a mis chaque outil dans une "boîte" isolée (un conteneur),
et Docker Compose démarre toutes les boîtes ensemble avec une seule commande.
""")

st.markdown("---")

st.subheader("🟢 Nos conteneurs en production")
try:
    st.image("app/images/docker_containers.png", caption="Tous les services tournent en simultané", use_container_width=True)
except FileNotFoundError:
    st.warning("Image docker_containers.png non trouvée.")

st.markdown("---")

st.header("Nos 9 services Docker")

st.markdown("Chaque service fait **une seule chose**. Ils communiquent entre eux via un réseau interne.")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🗄️ PostgreSQL")
        st.markdown("Base de données d'Airflow. Stocke l'historique des tâches automatiques.")

    with st.container(border=True):
        st.markdown("### 📊 MLflow")
        st.markdown("Enregistre chaque entraînement : métriques, paramètres, modèles. Notre journal de bord ML.")

    with st.container(border=True):
        st.markdown("### ⚡ FastAPI")
        st.markdown("Reçoit les demandes de prédiction (JSON) et répond avec le prix estimé.")

with col2:
    with st.container(border=True):
        st.markdown("### 🔒 Nginx")
        st.markdown("Protège l'accès à l'API. Redirige tout en HTTPS et bloque les requêtes trop nombreuses (max 10/seconde).")

    with st.container(border=True):
        st.markdown("### 🏠 Streamlit")
        st.markdown("L'interface utilisateur. Les pages que vous voyez maintenant.")

    with st.container(border=True):
        st.markdown("### 📡 Prometheus")
        st.markdown("Collecte les métriques de l'API toutes les 15 secondes automatiquement.")

with col3:
    with st.container(border=True):
        st.markdown("### 📈 Grafana")
        st.markdown("Affiche les métriques Prometheus sous forme de graphiques en temps réel.")

    with st.container(border=True):
        st.markdown("### ⚙️ Airflow Scheduler")
        st.markdown("Le planificateur : lance automatiquement les tâches selon le planning.")

    with st.container(border=True):
        st.markdown("### 🌐 Airflow Webserver")
        st.markdown("L'interface web d'Airflow pour visualiser et surveiller les DAGs.")

st.markdown("---")

st.header("Comment les services se parlent ?")

st.code("""
Utilisateur
    ↓
Streamlit (port 8501)  ← interface web
    ↓
FastAPI (port 8000)    ← prédiction XGBoost
    ↓
MLflow (port 5000)     ← chargement du modèle

En parallèle :
Prometheus → scrape FastAPI /metrics toutes les 15s
Grafana → affiche les métriques Prometheus
Airflow → orchestre les tâches automatiques (drift, retraining)
PostgreSQL → stocke les données Airflow
""", language="")

st.markdown("---")

st.header("🛠️ Orchestration avec Airflow")

st.markdown("""
Airflow est notre tour de contrôle. Il assure que chaque tâche s'exécute dans le bon ordre et au bon moment.
On a créé **2 DAGs** (pipelines automatiques) :
- **compagnon_immo_pipeline** : retraining hebdomadaire (collect → preprocess → train → reload)
- **drift_monitoring_retraining** : vérification quotidienne à 6h, retraining automatique si drift > 30%
""")

try:
    st.image("app/images/airflow_dags.png", caption="Les 2 pipelines automatiques dans Airflow", use_container_width=True)
except FileNotFoundError:
    st.warning("L'image airflow_dags.png est introuvable.")

AIRFLOW_URL = os.environ.get("AIRFLOW_URL", "http://localhost:8080")
st.markdown(f"**Accès Airflow en direct :** [http://localhost:8080]({AIRFLOW_URL})")

st.markdown("---")

st.header("⚙️ CI — Intégration Continue avec GitHub Actions")

st.markdown("""
À chaque fois qu'on pousse du code sur GitHub, un pipeline **CI (Continuous Integration)** se déclenche automatiquement.

**Ce qu'il fait :**
1. **Lint** avec Ruff → vérifie la qualité du code
2. **Tests unitaires** avec Pytest → vérifie que l'API répond correctement

Si un test échoue, le code n'est pas intégré. Ça garantit qu'on ne casse jamais ce qui marchait.
""")

try:
    st.image("app/images/github_actions.png", caption="42 runs CI — tous validés ✅", use_container_width=True)
except FileNotFoundError:
    st.warning("Image github_actions.png non trouvée.")

st.markdown("---")

st.header("🚀 Et demain ? Kubernetes")

st.markdown("""
Notre projet tourne aujourd'hui sur **une seule machine** avec Docker Compose.

Si le trafic augmente (des milliers d'utilisateurs), Docker Compose ne suffit plus.
La prochaine étape serait **Kubernetes** : il permet de faire tourner plusieurs copies de chaque service
et de les équilibrer automatiquement — c'est ce qu'on appelle le **scaling horizontal**.

Nous avons déjà préparé les fichiers de configuration Kubernetes (`k8s/`) dans notre repo.
""")

st.success("✅ Une seule commande pour tout démarrer : **docker compose up -d**")
