import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Infrastructure & Microservices", layout="wide")

# 2. FRISE DE PROGRESSION
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

render_pipeline_header("Infrastructure")

# 3. CONTENU
st.header("🐳 2. Infrastructure & Microservices")
st.markdown("### Construire un environnement reproductible")

# Colonne gauche (Schéma + Cartes) / Colonne droite (Docker PS)
col_l, col_r = st.columns([1.5, 1])

with col_l:
    st.subheader("Architecture Docker Compose")
    
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grille des 6 cartes
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**🐳 Docker**<br><small>Isolation des services.</small>", unsafe_allow_html=True)
        st.markdown("**📦 Docker Compose**<br><small>Orchestration locale.</small>", unsafe_allow_html=True)
    with c2:
        st.markdown("**⚡ FastAPI**<br><small>API REST haute performance.</small>", unsafe_allow_html=True)
        st.markdown("**🗄 PostgreSQL**<br><small>Persistance des données.</small>", unsafe_allow_html=True)
    with c3:
        st.markdown("**🧪 MLflow**<br><small>Tracking des modèles.</small>", unsafe_allow_html=True)
        st.markdown("**📈 Prometheus**<br><small>Monitoring temps réel.</small>", unsafe_allow_html=True)

with col_r:
    st.subheader("État du cluster")
    st.caption("Capture d'écran de l'environnement actif :")
    st.info("docker ps")
    # Simuler le tableau Docker PS propre
    st.table(pd.DataFrame({
        "CONTAINER": ["Frontend", "API-Gateway", "Inference", "MLflow", "Postgres", "Prometheus"],
        "STATUS": ["Up 2h", "Up 2h", "Up 2h", "Up 2h", "Up 5d", "Up 5d"]
    }))

# 4. BAS DE PAGE : POURQUOI ?
st.markdown("---")
st.subheader("Pourquoi une architecture microservices ?")
b1, b2, b3, b4 = st.columns(4)
b1.metric("Découplage", "Indépendance")
b2.metric("Évolutivité", "Scalable")
b3.metric("Maintenance", "Modulaire")
b4.metric("Déploiement", "Indépendant")

st.markdown("""
> L'approche microservices permet à chaque composant (API, ML, Monitoring) d'évoluer de manière autonome. 
> Cela réduit le risque de régression lors des mises à jour et facilite la maintenance en conditions réelles.
""")