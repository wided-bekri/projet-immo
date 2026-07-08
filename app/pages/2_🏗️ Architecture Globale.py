import streamlit as st

st.set_page_config(page_title="Architecture MLOps", layout="wide")

st.title("🏗️ Architecture MLOps — Compagnon Immobilier")
st.markdown("Vue d'ensemble du pipeline MLOps mis en place, de la donnée brute à la prédiction en production.")

st.markdown("---")

schema_html = """
<div style="font-family: Arial, sans-serif; padding: 10px;">

  <!-- LIGNE 1 : DONNÉES -->
  <div style="display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:10px;">
    <div style="background:#e8f4fd; border:2px solid #2196F3; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">📂</div>
      <div style="font-weight:bold; color:#1565C0;">Données DVF</div>
      <div style="font-size:0.8rem; color:#555;">4,48M transactions<br>+ 7 sources enrichies</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#fff3e0; border:2px solid #FF9800; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">📦</div>
      <div style="font-weight:bold; color:#E65100;">DVC + DagsHub</div>
      <div style="font-size:0.8rem; color:#555;">Versioning données<br>& modèles</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#f3e5f5; border:2px solid #9C27B0; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">⚙️</div>
      <div style="font-weight:bold; color:#6A1B9A;">Airflow</div>
      <div style="font-size:0.8rem; color:#555;">Orchestration<br>du pipeline</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#e8f5e9; border:2px solid #4CAF50; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">🤖</div>
      <div style="font-weight:bold; color:#2E7D32;">XGBoost</div>
      <div style="font-size:0.8rem; color:#555;">Entraînement<br>MAE 648 €/m²</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#fce4ec; border:2px solid #E91E63; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">📊</div>
      <div style="font-weight:bold; color:#880E4F;">MLflow</div>
      <div style="font-size:0.8rem; color:#555;">Tracking + Registry<br>alias "production"</div>
    </div>
  </div>

  <!-- FLÈCHE VERS LE BAS -->
  <div style="text-align:center; font-size:1.5rem; color:#999; margin:5px 0;">↓</div>

  <!-- LIGNE 2 : DÉPLOIEMENT -->
  <div style="display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:10px;">
    <div style="background:#e3f2fd; border:2px solid #1976D2; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">🐳</div>
      <div style="font-weight:bold; color:#0D47A1;">Docker</div>
      <div style="font-size:0.8rem; color:#555;">9 microservices<br>Docker Compose</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#fff8e1; border:2px solid #FFC107; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">🔒</div>
      <div style="font-weight:bold; color:#F57F17;">Nginx</div>
      <div style="font-size:0.8rem; color:#555;">Reverse proxy<br>HTTPS + rate limit</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#e8f5e9; border:2px solid #43A047; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">⚡</div>
      <div style="font-weight:bold; color:#1B5E20;">FastAPI</div>
      <div style="font-size:0.8rem; color:#555;">API /predict<br>/health /model/info</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#e8eaf6; border:2px solid #3F51B5; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">🏠</div>
      <div style="font-weight:bold; color:#1A237E;">Streamlit</div>
      <div style="font-size:0.8rem; color:#555;">Interface utilisateur<br>10 pages</div>
    </div>
  </div>

  <!-- FLÈCHE VERS LE BAS -->
  <div style="text-align:center; font-size:1.5rem; color:#999; margin:5px 0;">↓</div>

  <!-- LIGNE 3 : MONITORING -->
  <div style="display:flex; align-items:center; justify-content:center; gap:10px; margin-bottom:10px;">
    <div style="background:#fbe9e7; border:2px solid #FF5722; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">📡</div>
      <div style="font-weight:bold; color:#BF360C;">Prometheus</div>
      <div style="font-size:0.8rem; color:#555;">Métriques API<br>scrape 15s</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#f9fbe7; border:2px solid #CDDC39; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">📈</div>
      <div style="font-weight:bold; color:#827717;">Grafana</div>
      <div style="font-size:0.8rem; color:#555;">Dashboards<br>temps réel</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#e0f7fa; border:2px solid #00BCD4; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">🔍</div>
      <div style="font-weight:bold; color:#006064;">Evidently</div>
      <div style="font-size:0.8rem; color:#555;">Détection drift<br>2022 vs 2024/2025</div>
    </div>
    <div style="font-size:1.5rem; color:#999;">→</div>
    <div style="background:#f3e5f5; border:2px solid #9C27B0; border-radius:10px; padding:12px 20px; text-align:center; min-width:140px;">
      <div style="font-size:1.5rem;">🔄</div>
      <div style="font-weight:bold; color:#4A148C;">Retraining auto</div>
      <div style="font-size:0.8rem; color:#555;">Si drift > 30%<br>→ Airflow DAG</div>
    </div>
  </div>

</div>
"""

st.markdown(schema_html, unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Le projet en chiffres")
    st.markdown("""
    - **4,48M** transactions DVF analysées
    - **31** features par prédiction
    - **MAE 648 €/m²** — R² = 0.80
    - **9 microservices** Docker
    """)

with col2:
    st.markdown("### 🛠️ Stack technique")
    st.markdown("""
    - **Versioning** : DVC + DagsHub + Git
    - **Orchestration** : Airflow 2.9.1
    - **ML Tracking** : MLflow 3.14
    - **Serving** : FastAPI + Nginx HTTPS
    """)

with col3:
    st.markdown("### 🔄 Pipeline automatisé")
    st.markdown("""
    - Détection drift quotidienne
    - Retraining automatique si drift > 30%
    - Nouveau modèle → Registry MLflow
    - Rechargement API sans interruption
    """)
