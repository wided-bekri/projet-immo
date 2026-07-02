import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import streamlit.components.v1 as components

# ==================================================
# 1. CONFIGURATION DE LA PAGE
# ==================================================
st.set_page_config(
    page_title="Gouvernance & Versioning MLOps",
    page_icon="📦",
    layout="wide"
)

# Application du style CSS unifié
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE, "assets", "style.css")
if os.path.exists(CSS_FILE):
    with open(CSS_FILE, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ==================================================
# 2. BANDEAU NARRATIF GLOBAL
# ==================================================
components.html(
    """
    <div style="
        background: linear-gradient(135deg, #162447 0%, #a55eea 100%);
        padding: 25px 40px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 10px;
        font-family: Arial, sans-serif;
    ">
        <h1 style="color: #ffffff; margin: 0; font-size: 2.1rem; font-weight: 800;">
            📦 Cycle de Vie MLOps — Du Laboratoire à l'Industrialisation
        </h1>
        <div style="color: #00eaaf; margin-top: 8px; font-size: 1.1rem; font-weight: 400;">
            « Validation, traçabilité des données, gouvernance des modèles et isolation multi-conteneurs »
        </div>
    </div>
    """,
    height=130
)

# ==================================================
# 3. PANORAMA DES PHASES (SYNTHÈSE JURY)
# ==================================================
st.markdown("### 🏛️ Synthèse des Étapes Clés (Soutenance du 7 Juillet 2026)")

c_p1, c_p2 = st.columns(2)

with c_p1:
    with st.container(border=True):
        st.markdown("#### 🚀 Phase 1 : Les Fondations Logicielles")
        st.markdown("""
        * **Hygiène Globale :** Gestion de l'historique de code avec **Git/GitHub**, isolation des dépendances dans `requirements.txt` et exclusion des données/secrets via `.gitignore`.
        * **Pipeline ML Baseline :** Script `train_model.py` (Pandas, découpage 80/20 Train/Test), entraînement d'un **RandomForestRegressor** (100 arbres) évalué via les métriques **MAE** et **R²**.
        * **Contrat d'Interface :** Serveur asynchrone **Uvicorn**, validation typologique stricte par **Pydantic** (`schemas.py`) et tests unitaires automatisés avec **Pytest**.
        """)
        st.caption("🎯 Résultat : Un code propre, documenté et testé en local.")

with c_p2:
    with st.container(border=True):
        st.markdown("#### 📦 Phase 2 : Industrialisation & Gouvernance")
        st.markdown("""
        * **Tour de Contrôle MLflow :** Suivi automatisé des paramètres d'entraînement (**Tracking**) et mise à jour transparente des modèles en production via le **Model Registry** (alias `@production`).
        * **Isolation Docker :** Encapsulation de l'API et de ses dépendances dans des conteneurs pour éradiquer les conflits d'environnements.
        * **Gouvernance des Données :** Déploiement de **DVC & DagsHub** pour versionner les fichiers lourds (CSV) impossibles à stocker sur Git.
        """)
        st.caption("🎯 Résultat : Une architecture microservices reproductible et découplée.")

st.write("---")

# ==================================================
# 4. FOCUS TECHNIQUE : DATA VERSIONING (DVC + DAGSHUB)
# ==================================================
st.markdown("### 🛡️ Le Versioning des Données : Le couple DVC + DagsHub")
st.caption("Pourquoi et comment l'équipe protège et trace le patrimoine de données volumineuses du projet.")

c_dvc_desc, c_dvc_mecanisme = st.columns([1.1, 0.9])

with c_dvc_desc:
    st.markdown("##### 💡 Le Problème de Git face aux Volumes")
    st.info("""
    Git est parfait pour le code textuel, mais il sature et refuse les fichiers lourds de plus de 100 Mo. Notre jeu de données immobilières contenant des millions de lignes ne peut pas être poussé directement sur GitHub.
    
    **La Solution DVC (Data Version Control) :** DVC est le "Git des données". Il surveille les fichiers lourds, génère un petit fichier de métadonnées (ex: `immobilier.csv.dvc`) contenant une empreinte numérique unique (**Hash MD5**). Git se charge uniquement de versionner ce petit fichier de pointeur.
    """)
    st.success("☁️ **DagsHub :** Il fait office de serveur distant de stockage (Remote Storage) hautement sécurisé pour accueillir nos vrais volumes de données physiques.")

with c_dvc_mecanisme:
    st.markdown("**Fichiers de Configuration Générés par l'équipe (`.dvc/config`) :**")
    st.code("""
[core]
    analytics = false
    remote = origin
['remote "origin"']
    url = https://dagshub.com/wided-bekri/projet-immo.dvc
    """, language="ini")
    st.markdown("**La commande magique de reproductibilité complète :**")
    st.code("""
# Récupérer la version exacte du code et du dataset associés
git checkout master
dvc pull -r origin
    """, language="bash")

st.write("---")

# ==================================================
# 5. L'ÉCOSYSTÈME DE PRODUCTION DOCKER COMPOSE
# ==================================================
st.markdown("### 🔌 L'Écosystème de Production final (10 Microservices)")
st.caption("Notre architecture logicielle isolée, résiliente et distribuée définie dans docker-compose.yml.")

service_selection = st.selectbox(
    "👉 Sélectionnez un pôle de l'infrastructure pour l'exposer au jury :",
    [
        "🧠 Pôle Intelligence & API (FastAPI, MLflow)",
        "🛡️ Pôle Sécurité & Entrée (Nginx Proxy)",
        "🔄 Pôle Orchestration de Données (Apache Airflow, Postgres)",
        "📈 Pôle Métriques & Supervision (Prometheus, Grafana)"
    ]
)

c_dock_code, c_dock_desc = st.columns([1.1, 0.9])

with c_dock_code:
    if "Intelligence" in service_selection:
        st.code("""
  api:
    build:
      context: .
      dockerfile: dockerfiles/Dockerfile.inference
    container_name: immo-api
    expose:
      - "8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - IMMO_API_KEY=${IMMO_API_KEY:-}
    depends_on:
      mlflow:
        condition: service_healthy
        
  mlflow:
    container_name: immo-mlflow
    ports:
      - "5000:5000"
    volumes:
      - mlflow_db:/mlflow
      - mlflow_artifacts:/mlflow/artifacts
        """, language="yaml")
        
    elif "Sécurité" in service_selection:
        st.code("""
  nginx:
    build:
      context: deployments/nginx/
      dockerfile: Dockerfile
    container_name: immo-nginx
    ports:
      - "80:80"   # Entrée HTTP standard
      - "443:443" # Entrée HTTPS sécurisée
    depends_on:
      api:
        condition: service_healthy
        """, language="yaml")
        
    elif "Orchestration" in service_selection:
        st.code("""
  postgres:
    image: postgres:15
    container_name: immo-postgres
    environment:
      - POSTGRES_DB=airflow
      
  airflow-webserver:
    image: apache/airflow:2.9.1-python3.11
    ports:
      - "8080:8080" # Administration des tâches (DAGs)
    command: airflow webserver
    depends_on:
      postgres:
        condition: service_healthy
        """, language="yaml")
        
    elif "Supervision" in service_selection:
        st.code("""
  prometheus:
    image: prom/prometheus:latest
    container_name: immo-prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: immo-grafana
    ports:
      - "3000:3000"
        """, language="yaml")

with c_dock_desc:
    if "Intelligence" in service_selection:
        st.markdown("##### 🧠 Le Cerveau Applicatif")
        st.info("""
        * **Découplage :** Le conteneur `immo-api` n'embarque plus de fichier de modèle figé en dur. Il interroge dynamiquement le registre centralisé `immo-mlflow` pour charger la version `@production`.
        * **Surveillance d'état :** L'API intègre une vérification de sa route de santé (`/health`) pour permettre à Docker de la redémarrer automatiquement en cas de défaillance.
        """)
        
    elif "Sécurité" in service_selection:
        st.markdown("##### 🛡️ Le Reverse Proxy (Nginx)")
        st.info("""
        * **Rôle :** Unique porte d'entrée publique de notre écosystème.
        * **Intérêt Pro :** Protège l'API FastAPI des attaques extérieures en masquant son port réel (`8000`). Nginx intercepte le trafic sur le port web standard (`80/443`) et distribue les requêtes de manière sécurisée.
        """)
        
    elif "Orchestration" in service_selection:
        st.markdown("##### 🔄 L'Usine de Pipeline Automatisée (Airflow)")
        st.info("""
        * **Apache Airflow :** Gère l'automatisation et la planification de nos scripts de traitement et de réentraînement (DAGs).
        * **Persistance :** S'appuie sur une base de données relationnelle **PostgreSQL** dédiée pour enregistrer l'état et l'historique d'exécution de nos flux.
        """)
        
    elif "Supervision" in service_selection:
        st.markdown("##### 📈 La Tour de Contrôle Technique")
        st.info("""
        * **Prometheus :** Collecte en temps réel les performances système et applicatives (ex: temps de réponse de l'API de prédiction).
        * **Grafana :** Transforme ces données brutes de télémétrie en graphiques visuels et lisibles pour les administrateurs du système.
        """)

# ==================================================
# 🚀 ANCRAGE DE TRANSITION VISUELLE
# ==================================================
st.write("---")
st.markdown(f"""
<div style="background: linear-gradient(135deg, #162447 0%, #1f4068 100%); padding: 20px; border-radius: 10px; border-left: 6px solid #a55eea;">
    <h4 style="color:#00eaaf !important; margin-top:0; font-weight:700; font-size:1.1rem;">🔄 Transition : Vers l'orchestration des flux et pipelines automatisés</h4>
    <p style="font-size:0.9rem; margin-bottom:0; opacity:0.95; line-height:1.5;">
        <b>« Messieurs les membres du jury, notre infrastructure logicielle est désormais totalement isolée, gouvernée et versionnée (Code via GitHub, Données via DVC/DagsHub, Modèles via MLflow).</b><br>
        Cependant, un système en production doit savoir vivre et s'actualiser de lui-même sans intervention humaine manuelle.<br>
        Voyons immédiatement dans la <b>Phase 3</b> comment nous exploitons la puissance d'<b>Apache Airflow</b> pour orchestrer nos pipelines de données et planifier nos cycles d'entraînement ! »
    </p>
</div>
""", unsafe_allow_html=True)