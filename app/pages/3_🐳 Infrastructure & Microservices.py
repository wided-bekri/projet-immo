import streamlit as st

st.set_page_config(page_title="Infrastructure", layout="wide")

st.title("🐳 Infrastructure & Microservices")

st.markdown("""
**Le problème qu'on avait :** comment faire tourner le projet de la même façon sur ma machine,
sur la machine de Carine, et demain sur un serveur ?

**La solution :** Docker. On a mis chaque outil dans une "boîte" isolée (un conteneur),
et Docker Compose démarre toutes les boîtes ensemble avec une seule commande.
""")

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

st.success("✅ Une seule commande pour tout démarrer : **docker compose up -d**")

st.info("""
💡 **Pourquoi c'est utile ?**
Si le service FastAPI plante, Streamlit continue de fonctionner.
Si Prometheus plante, l'API continue de faire des prédictions.
Chaque service est indépendant → moins de risque de tout casser d'un coup.
""")
