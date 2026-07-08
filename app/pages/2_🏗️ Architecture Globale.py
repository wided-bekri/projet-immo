import streamlit as st

# 1. CONFIGURATION
st.set_page_config(page_title="Architecture MLOps", layout="wide")

# 2. FONCTION FRISE (À placer dans chaque page MLOps)
def render_pipeline_header(active_step):
    steps = ["Infrastructure", "Orchestration", "Versioning", "Déploiement", "Monitoring"]
    html_content = '<div style="display: flex; justify-content: space-between; align-items: center; background: #f8f9fa; padding: 15px 20px; border-radius: 8px; border: 1px solid #dee2e6; margin-bottom: 30px;">'
    for i, step in enumerate(steps):
        is_active = (step == active_step)
        color = "#17b978" if is_active else "#6c757d"
        weight = "bold" if is_active else "normal"
        html_content += f'<div style="text-align: center; color: {color}; font-weight: {weight}; font-size: 0.9rem;">{step}</div>'
        if i < len(steps) - 1:
            html_content += '<div style="color: #dee2e6;">➔</div>'
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)

# 3. CONTENU PAGE 1
render_pipeline_header("Infrastructure")

st.header("🏗️ 1. Architecture Globale : Vision MLOps")
st.markdown("Vue d'ensemble de l'écosystème technique garantissant reproductibilité et scalabilité.")

col_schema, col_desc = st.columns([2, 1])

with col_schema:
    # Insère ici ton schéma ou une explication visuelle
    st.info("Visualisation de l'architecture : Flux de données, conteneurs et interconnexions.")
    

with col_desc:
    st.subheader("Composants Clés")
    st.markdown("""
    * **Data Layer :** Stockage S3 & DVC
    * **Compute Layer :** Orchestration Docker
    * **ML Layer :** Registry & Experiment Tracking
    * **Serving Layer :** API haute performance
    """)

st.markdown("---")
st.markdown("Le système repose sur le principe de **Pipeline as Code**. Chaque modification déclenche un cycle automatisé de validation.")