"""
Page 3 - MLOps Pipeline : Orchestration & Monitoring
Compagnon Immobilier
"""
import streamlit as st
import requests
import os
import streamlit.components.v1 as components

st.set_page_config(
    page_title="MLOps Pipeline - Compagnon Immobilier",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE, "assets")

with open(os.path.join(ASSET_DIR, "style.css"), encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# ─── URLs internes Docker ─────────────────────────────────────────────────────
AIRFLOW_URL    = os.environ.get("AIRFLOW_URL",    "http://airflow-webserver:8080")
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
API_URL        = os.environ.get("API_URL",        "http://api:8000")

# ─── Header ───────────────────────────────────────────────────────────────────
components.html("""
<div style="
    background: linear-gradient(135deg, #0f2027 0%, #1a3a4a 50%, #00eaaf22 100%);
    padding: 35px 40px; border-radius: 14px; text-align: center;
    font-family: Arial, sans-serif; box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    margin-bottom: 10px;
">
    <div style="color:#ffffff; font-size:2.4rem; font-weight:800;">
        ⚙️ MLOps Pipeline — De la Data à la Production
    </div>
    <div style="color:#00eaaf; margin-top:12px; font-size:1.1rem;">
        Orchestration Airflow · Monitoring Prometheus/Grafana · API FastAPI en production
    </div>
    <div style="width:50%; height:1px; background:rgba(255,255,255,0.2); margin:18px auto;"></div>
    <div style="color:#ffffff; font-size:1rem; opacity:0.9; font-style:italic;">
        « Un modèle non supervisé en production n'est pas un système MLOps — c'est une bombe à retardement. »
    </div>
</div>
""", height=200)

# ─── Vue d'ensemble ───────────────────────────────────────────────────────────
st.markdown("## 🗺️ Architecture MLOps complète")

col_p3, col_p4 = st.columns(2)

with col_p3:
    with st.container(border=True):
        st.markdown("### ⛓️ Phase 3 — Orchestration")
        st.markdown("""
        **Apache Airflow** automatise nos pipelines de données :
        - 🔄 **DAG retraining** : réentraînement hebdomadaire du modèle XGBoost
        - 📥 **DAG ingestion** : ingestion des nouvelles transactions DVF
        - 🔍 **DAG monitoring** : calcul des métriques de dérive

        Sans orchestration, chaque mise à jour du modèle nécessiterait une intervention manuelle.
        """)
        st.caption("🎯 Résultat : pipeline automatisé, traçable et reproductible")

with col_p4:
    with st.container(border=True):
        st.markdown("### 🛡️ Phase 4 — Monitoring")
        st.markdown("""
        **Prometheus + Grafana** supervisent le système en temps réel :
        - 📊 **Métriques API** : nombre de prédictions, latence, erreurs
        - 🚨 **Alertes** : seuils de performance et de disponibilité
        - 📈 **Dashboards** : visualisation des KPIs techniques

        Sans monitoring, une dégradation du modèle serait invisible jusqu'à la plainte client.
        """)
        st.caption("🎯 Résultat : observabilité totale du système en production")

st.write("---")

# ─── Statut en direct ─────────────────────────────────────────────────────────
st.markdown("## 🟢 Statut des services en temps réel")

def check_service(url, path="/", timeout=2):
    try:
        r = requests.get(url + path, timeout=timeout)
        return r.status_code < 400, r.status_code
    except Exception as e:
        return False, str(e)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    ok, code = check_service(API_URL, "/health")
    status = "🟢 En ligne" if ok else "🔴 Hors ligne"
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;background:#F8FAFC;border-radius:10px;border:1px solid #E2E8F0">
        <p style="font-size:1.5rem;margin:0">🚀</p>
        <p style="font-weight:700;margin:0.3rem 0;color:#1B3A4B">FastAPI</p>
        <p style="margin:0;font-size:0.85rem">{status}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    ok, code = check_service("http://mlflow:5000", "/health")
    status = "🟢 En ligne" if ok else "🔴 Hors ligne"
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;background:#F8FAFC;border-radius:10px;border:1px solid #E2E8F0">
        <p style="font-size:1.5rem;margin:0">📦</p>
        <p style="font-weight:700;margin:0.3rem 0;color:#1B3A4B">MLflow</p>
        <p style="margin:0;font-size:0.85rem">{status}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    ok, code = check_service(AIRFLOW_URL, "/health")
    status = "🟢 En ligne" if ok else "🔴 Hors ligne"
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;background:#F8FAFC;border-radius:10px;border:1px solid #E2E8F0">
        <p style="font-size:1.5rem;margin:0">⛓️</p>
        <p style="font-weight:700;margin:0.3rem 0;color:#1B3A4B">Airflow</p>
        <p style="margin:0;font-size:0.85rem">{status}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    ok, code = check_service(PROMETHEUS_URL, "/-/healthy")
    status = "🟢 En ligne" if ok else "🔴 Hors ligne"
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;background:#F8FAFC;border-radius:10px;border:1px solid #E2E8F0">
        <p style="font-size:1.5rem;margin:0">📈</p>
        <p style="font-weight:700;margin:0.3rem 0;color:#1B3A4B">Prometheus</p>
        <p style="margin:0;font-size:0.85rem">{status}</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    ok, code = check_service("http://grafana:3000", "/api/health")
    status = "🟢 En ligne" if ok else "🔴 Hors ligne"
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;background:#F8FAFC;border-radius:10px;border:1px solid #E2E8F0">
        <p style="font-size:1.5rem;margin:0">📊</p>
        <p style="font-weight:700;margin:0.3rem 0;color:#1B3A4B">Grafana</p>
        <p style="margin:0;font-size:0.85rem">{status}</p>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# ─── Métriques Prometheus en direct ──────────────────────────────────────────
st.markdown("## 📊 Métriques de production (Prometheus)")

def prom_query(metric):
    try:
        r = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": metric}, timeout=3
        )
        data = r.json()
        results = data.get("data", {}).get("result", [])
        if results:
            return float(results[0]["value"][1])
        return None
    except:
        return None

predictions_total = prom_query("immo_predictions_total")
latency_avg       = prom_query("rate(immo_prediction_latency_seconds_sum[5m]) / rate(immo_prediction_latency_seconds_count[5m])")
errors_total      = prom_query("immo_prediction_errors_total")

m1, m2, m3, m4 = st.columns(4)

with m1:
    val = f"{int(predictions_total):,}" if predictions_total is not None else "N/A"
    st.metric("🎯 Prédictions totales", val)

with m2:
    val = f"{latency_avg*1000:.1f} ms" if latency_avg is not None else "N/A"
    st.metric("⚡ Latence moyenne (5m)", val)

with m3:
    val = f"{int(errors_total)}" if errors_total is not None else "N/A"
    st.metric("❌ Erreurs totales", val)

with m4:
    if predictions_total is not None and errors_total is not None and predictions_total > 0:
        taux = (1 - errors_total / predictions_total) * 100
        val = f"{taux:.1f}%"
    else:
        val = "N/A"
    st.metric("✅ Taux de succès", val)

if predictions_total is None:
    st.info("ℹ️ Prometheus n'est pas encore joignable depuis ce conteneur — les métriques seront disponibles une fois les services démarrés.")

st.write("---")

# ─── Airflow DAGs ──────────────────────────────────────────────────────────────
st.markdown("## ⛓️ Orchestration Airflow — Les DAGs du projet")

tab_dag1, tab_dag2, tab_dag3 = st.tabs(["🔄 Réentraînement", "📥 Ingestion DVF", "🏗️ Architecture"])

with tab_dag1:
    col_code, col_desc = st.columns([1.2, 0.8])
    with col_code:
        st.markdown("**DAG : `retrain_model`**")
        st.code("""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'compagnon-immo',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='retrain_model',
    default_args=default_args,
    schedule_interval='@weekly',
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    train = PythonOperator(
        task_id='train_xgboost',
        python_callable=train_model,
    )

    evaluate = PythonOperator(
        task_id='evaluate_model',
        python_callable=evaluate_model,
    )

    promote = PythonOperator(
        task_id='promote_to_production',
        python_callable=promote_model,
    )

    train >> evaluate >> promote
        """, language="python")

    with col_desc:
        st.markdown("##### 🎯 Objectif")
        st.info("""
        Ce DAG automatise le cycle de vie du modèle XGBoost :

        1. **Train** : Réentraîne sur les données DVF les plus récentes
        2. **Evaluate** : Compare les métriques (MAE, R², MAPE) avec le modèle en production
        3. **Promote** : Si les métriques s'améliorent → met à jour l'alias `@production` dans MLflow

        **Fréquence :** Hebdomadaire (chaque lundi à 2h00)
        """)
        st.success("✅ Sans ce DAG, le modèle se dégraderait sans qu'on le sache.")

with tab_dag2:
    col_code2, col_desc2 = st.columns([1.2, 0.8])
    with col_code2:
        st.markdown("**DAG : `ingest_dvf`**")
        st.code("""
with DAG(
    dag_id='ingest_dvf',
    schedule_interval='@monthly',
    start_date=datetime(2025, 1, 1),
) as dag:

    download = PythonOperator(
        task_id='download_dvf',
        python_callable=download_dvf_data,
    )

    clean = PythonOperator(
        task_id='clean_and_enrich',
        python_callable=clean_and_enrich,
    )

    push_dvc = BashOperator(
        task_id='push_to_dvc',
        bash_command='dvc add data/raw/dvf.csv && dvc push',
    )

    download >> clean >> push_dvc
        """, language="python")

    with col_desc2:
        st.markdown("##### 🎯 Objectif")
        st.info("""
        Ce DAG maintient notre dataset à jour :

        1. **Download** : Télécharge les nouvelles transactions DVF depuis data.gouv.fr
        2. **Clean** : Nettoie, filtre les outliers et enrichit avec Filosofi/BPE
        3. **Push DVC** : Versionne les nouvelles données sur DagsHub

        **Fréquence :** Mensuelle (les données DVF sont publiées tous les trimestres)
        """)

with tab_dag3:
    st.markdown("##### 📐 Architecture du pipeline complet")
    components.html("""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap;">
            <div style="background:#1B3A4B;color:white;padding:12px 16px;border-radius:8px;text-align:center;min-width:100px">
                <div style="font-size:1.3rem">📥</div>
                <b>DVF Raw</b><br><small>data.gouv.fr</small>
            </div>
            <div style="font-size:1.5rem;color:#64748B">→</div>
            <div style="background:#2E86AB;color:white;padding:12px 16px;border-radius:8px;text-align:center;min-width:100px">
                <div style="font-size:1.3rem">🧹</div>
                <b>Clean & Enrich</b><br><small>Airflow DAG</small>
            </div>
            <div style="font-size:1.5rem;color:#64748B">→</div>
            <div style="background:#17b978;color:white;padding:12px 16px;border-radius:8px;text-align:center;min-width:100px">
                <div style="font-size:1.3rem">📦</div>
                <b>DVC Push</b><br><small>DagsHub</small>
            </div>
            <div style="font-size:1.5rem;color:#64748B">→</div>
            <div style="background:#8B5CF6;color:white;padding:12px 16px;border-radius:8px;text-align:center;min-width:100px">
                <div style="font-size:1.3rem">🤖</div>
                <b>XGBoost Train</b><br><small>Airflow DAG</small>
            </div>
            <div style="font-size:1.5rem;color:#64748B">→</div>
            <div style="background:#F59E0B;color:white;padding:12px 16px;border-radius:8px;text-align:center;min-width:100px">
                <div style="font-size:1.3rem">📊</div>
                <b>MLflow Track</b><br><small>Registry</small>
            </div>
            <div style="font-size:1.5rem;color:#64748B">→</div>
            <div style="background:#EF4444;color:white;padding:12px 16px;border-radius:8px;text-align:center;min-width:100px">
                <div style="font-size:1.3rem">🚀</div>
                <b>FastAPI Prod</b><br><small>@production</small>
            </div>
        </div>
        <div style="text-align:center;margin-top:15px;color:#64748B;font-size:0.85rem">
            ↕ Prometheus collecte les métriques à chaque étape · Grafana les visualise
        </div>
    </div>
    """, height=160)

st.write("---")

# ─── Docker Compose — 10 services ─────────────────────────────────────────────
st.markdown("## 🐳 Infrastructure Docker — 10 Microservices")

services = [
    ("🚀", "immo-api",                 "FastAPI",         "Port 8000", "Inférence XGBoost + endpoints Prometheus"),
    ("📦", "immo-mlflow",              "MLflow",          "Port 5000", "Tracking des expériences + Model Registry"),
    ("🛡️", "immo-nginx",               "Nginx",           "Port 80/443", "Reverse proxy — point d'entrée unique"),
    ("⛓️", "immo-airflow-webserver",   "Airflow Web",     "Port 8080", "Interface de gestion des DAGs"),
    ("⚙️", "immo-airflow-scheduler",   "Airflow Sched",   "Interne",   "Planificateur des tâches automatisées"),
    ("🗄️", "immo-postgres",            "PostgreSQL",      "Interne",   "Base de données Airflow"),
    ("📈", "immo-prometheus",          "Prometheus",      "Port 9090", "Collecte des métriques temps réel"),
    ("📊", "immo-grafana",             "Grafana",         "Port 3000", "Dashboards de monitoring"),
    ("🔴", "immo-redis",               "Redis",           "Interne",   "Broker de messages Airflow (CeleryExecutor)"),
    ("🎨", "immo-streamlit",           "Streamlit",       "Port 8501", "Application de démonstration (cette page)"),
]

header_cols = st.columns([0.5, 1.5, 1, 1, 3])
header_cols[0].markdown("**#**")
header_cols[1].markdown("**Conteneur**")
header_cols[2].markdown("**Service**")
header_cols[3].markdown("**Accès**")
header_cols[4].markdown("**Rôle**")
st.markdown("<hr style='margin:0.3rem 0'>", unsafe_allow_html=True)

for i, (icon, container, service, port, role) in enumerate(services, 1):
    cols = st.columns([0.5, 1.5, 1, 1, 3])
    cols[0].markdown(f"**{i}**")
    cols[1].markdown(f"{icon} `{container}`")
    cols[2].markdown(service)
    cols[3].markdown(f"`{port}`")
    cols[4].markdown(role)
    st.markdown("<hr style='margin:0.2rem 0;opacity:0.3'>", unsafe_allow_html=True)

st.write("---")

# ─── Transition ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#0f2027,#1a3a4a);padding:22px;border-radius:10px;border-left:6px solid #00eaaf;">
    <h4 style="color:#00eaaf !important;margin-top:0;font-weight:700;">🔄 Transition : Vers la modélisation et la démonstration live</h4>
    <p style="color:#ffffff;font-size:0.92rem;margin-bottom:0;line-height:1.6;">
        <b>« Notre infrastructure MLOps est opérationnelle : les données sont versionnées (DVC),
        les modèles trackés (MLflow), les pipelines orchestrés (Airflow) et la production supervisée (Prometheus/Grafana).</b><br>
        Découvrons maintenant le modèle XGBoost que cette infrastructure entraîne et déploie automatiquement,
        puis testons notre outil d'estimation immobilière en conditions réelles. »
    </p>
</div>
""", unsafe_allow_html=True)
