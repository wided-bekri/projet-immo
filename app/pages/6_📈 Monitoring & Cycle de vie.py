import streamlit as st
import requests
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Monitoring & Cycle de vie", layout="wide")

st.title("📈 Monitoring & Cycle de vie")

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
