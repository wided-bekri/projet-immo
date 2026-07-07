import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Déploiement & Inférence", layout="wide")

# 2. FONCTION FRISE
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

render_pipeline_header("Déploiement")

# 3. CONTENU PAGE 4
st.header("🚀 4. Déploiement & Inférence")

# --- SECTION REGISTRY & GOUVERNANCE ---
st.subheader("📦 Gouvernance & Model Registry")
st.markdown("Gestion des versions et promotion vers la production via alias MLflow.")

df_registry = pd.DataFrame({
    "Version": ["v4", "v3", "v2"],
    "Alias MLflow": ["@champion (Prod)", "@challenger", "Archivé"],
    "Statut": ["Actif", "Test A/B", "Inactif"],
    "Date": ["Aujourd'hui", "Hier", "Il y a 2 semaines"]
})
st.table(df_registry)
st.info("💡 **Avantage :** Le basculement de l'alias `@champion` met à jour la production sans modifier le code de l'application.")

st.markdown("---")

# --- SECTION DÉPLOIEMENT ---
col_schema, col_swagger = st.columns([1.5, 1])

with col_schema:
    st.subheader("Workflow de prédiction")
    st.markdown("""
    1. **Utilisateur** (Interface Streamlit)
    2. ↓ **FastAPI Gateway**
    3. ↓ **Préprocessing** (Nettoyage & Encodage)
    4. ↓ **XGBoost Inférence** (Chargement modèle)
    5. ↓ **Réponse JSON** (Prédiction estimée)
    """)
    

with col_swagger:
    st.subheader("Documentation Swagger")
    st.info("Interface interactive pour tester les endpoints.")
    

st.markdown("---")

# 4. CYCLE & CARACTÉRISTIQUES
col_cycle, col_carac = st.columns(2)

with col_cycle:
    st.subheader("⏱️ Cycle d'une requête HTTP")
    st.markdown("""
    ① **Requête HTTP** (JSON payload) ➔ ② **Validation** (Pydantic) ➔ ③ **Préprocessing** ➔ ④ **Chargement** ➔ ⑤ **Inférence** ➔ ⑥ **Réponse**
    """)

with col_carac:
    st.subheader("Caractéristiques techniques")
    st.markdown("""
    * ✅ **API REST :** Standard de communication.
    * ✅ **Doc Swagger :** Intégration `/docs` auto.
    * ✅ **Performance :** Temps de réponse < 200ms.
    * ✅ **Validation :** Intégrité stricte via Pydantic.
    """)

# 5. SCRIPT ORAL FINAL
st.write("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #111e2e 0%, #1f4068 100%); padding: 18px; border-radius: 10px; border-left: 6px solid #ff9f43;">
    <h4 style="color:#ff9f43 !important; margin-top:0; font-weight:700;">🔄 Transition vers le Monitoring</h4>
    <p style="font-size:0.95rem; line-height:1.5; color:#ffffff;">
        <i>« Après avoir validé notre architecture et packagé notre modèle, nous assurons son intégrité opérationnelle. 
        Pour conclure, voyons comment nous surveillons la santé de ce système en temps réel pour garantir sa fiabilité 
        sur le long terme : place au Monitoring et à la gestion du cycle de vie. »</i>
    </p>
</div>
""", unsafe_allow_html=True)