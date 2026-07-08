import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 1. CONFIGURATION
st.set_page_config(page_title="Monitoring & Cycle de vie", layout="wide")

# ── Style Dashboard ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.section-title { font-size: 1.3rem; font-weight: 700; color: #00eaaf; margin: 24px 0 12px 0; border-bottom: 1px solid #0f3460; padding-bottom: 6px; }
.metric-card { background: #0e1117; padding: 15px; border-radius: 8px; border: 1px solid #262730; }
</style>
""", unsafe_allow_html=True)

# 2. FRISE DE PROGRESSION
def render_pipeline_header(active_step):
    steps = ["Infrastructure", "Orchestration", "Versioning", "Déploiement", "Monitoring"]
    html_content = '<div style="display: flex; justify-content: space-between; align-items: center; background: #f8f9fa; padding: 15px 20px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 30px;">'
    for i, step in enumerate(steps):
        is_active = (step == active_step)
        color = "#17b978" if is_active else "#6c757d"
        html_content += f'<div style="text-align: center; color: {color}; font-weight: {"bold" if is_active else "normal"};">{step}</div>'
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

render_pipeline_header("Monitoring")

# 3. HEADER & PHILOSOPHIE
st.header("📈 5. Monitoring & Cycle de vie")
st.markdown("> « Un projet MLOps ne s'arrête pas au meilleur modèle : il garantit sa fiabilité et sa performance tout au long de son cycle de vie en conditions réelles. »")

tab1, tab2, tab3 = st.tabs(["🔴 Métriques API (Prometheus)", "🔍 Drift & Qualité (Evidently)", "⚙️ Gouvernance & Stack"])

# --- TAB 1 : METRIQUES API ---
with tab1:
    st.markdown('<div class="section-title">Métriques API — Prometheus</div>', unsafe_allow_html=True)
    # Ici, ton code Prometheus (KPIs, santé, architecture)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🟢 Statut API", "OK")
    c2.metric("📨 Prédictions", "0")
    c3.metric("❌ Erreurs", "0")
    c4.metric("⚡ Latence P95", "145 ms")
    c5.metric("📈 Req/min", "0.0")
    
    st.info("**Modèle en production :** compagnon-immobilier | v: pkl-local | R²: 0.795 | MAE: 648€/m²")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Architecture :**")
        st.code("FastAPI /metrics ──scrape 15s──▶ Prometheus :9090 ──▶ Grafana :3000")
    with col_b:
        st.markdown("**Alertes :** 🔴 API down > 1 min | 🟡 Erreurs > 5% | 🟡 Latence P95 > 2s")

# --- TAB 2 : DRIFT & PIPELINE ---
with tab2:
    st.markdown('<div class="section-title">Détection de drift — Evidently</div>', unsafe_allow_html=True)
    st.write("Comparaison 2022 (Ref) vs 2024/2025. Si drift détecté → retraining déclenché.")
    
    # Intégration de la partie Evidently (Bouton, Rapports, Pipeline)
    col_btn1, col_btn2 = st.columns([3, 1])
    if col_btn2.button("🚀 Générer rapport drift"):
        st.write("Calcul du drift en cours...")
    
    # Types de drift + Pipeline
    st.markdown('<div class="section-title">Pipeline de retraining</div>', unsafe_allow_html=True)
    st.code("Données Prod ──▶ Evidently ──▶ Drift > seuil ──▶ Airflow DAG ──▶ Retrain ──▶ Reload Model")
    st.success("Seuils : Drift > 30% (Warning) | Drift > 50% (Retraining Auto)")

# --- TAB 3 : STACK & ACCÈS ---
with tab3:
    st.markdown('<div class="section-title">Accès & Stack technique</div>', unsafe_allow_html=True)
    
    # Grille des outils
    cols = st.columns(2)
    tools = [("📊 Grafana", "http://localhost:3000", "admin/admin"), ("🔥 Prometheus", "http://localhost:9090", "Direct"), 
             ("🌊 MLflow", "http://localhost:5000", "Direct"), ("🌀 Airflow", "http://localhost:8080", "admin/admin")]
    for i, (name, url, cred) in enumerate(tools):
        cols[i % 2].markdown(f"**{name}** 🔗 [Lien]({url}) | 🔑 `{cred}`")
    
    st.table(pd.DataFrame({
        "Composant": ["FastAPI", "Prometheus", "Grafana", "Evidently", "Airflow", "MLflow", "PostgreSQL", "Nginx", "Streamlit"],
        "Rôle": ["API", "Collecte", "Dashboards", "Drift", "Orchestration", "Registry", "BDD", "Proxy", "Interface"],
        "Port": ["8000", "9090", "3000", "-", "8080", "5000", "5432", "80/443", "8501"]
    }))

# 4. CONCLUSION FINALE
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-around; background: #2c3e50; color: white; padding: 20px; border-radius: 8px;">
    <div>Build ➔ Train ➔ Deploy ➔ Monitor ➔ Improve ↺</div>
</div>
""", unsafe_allow_html=True)