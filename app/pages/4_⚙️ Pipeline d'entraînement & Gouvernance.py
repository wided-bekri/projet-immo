import streamlit as st

# 1. CONFIGURATION
st.set_page_config(page_title="Pipeline & Gouvernance", layout="wide")

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

render_pipeline_header("Versioning")

# 3. BANDEAU D'INTRODUCTION (Adapté)
st.markdown("""
<div style="background: linear-gradient(135deg, #0f2027 0%, #203a43 100%); padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 25px;">
    <h1 style="color: #ffffff; margin: 0;">⚙️ Pipeline d'entraînement & Gouvernance</h1>
    <p style="color: #00eaaf; margin-top: 10px; font-weight: 400;">Optimisation systématique et traçabilité du cycle de vie ML</p>
</div>
""", unsafe_allow_html=True)

# 4. FIL D'ARIANE (Automatisation)
st.markdown("""
<div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 25px;">
    <div style="display: flex; justify-content: center; align-items: center; gap: 15px; font-size: 0.9rem; font-weight: bold;">
        <span style="color: #17b978;">📐 Target Engineering</span> ➔
        <span style="color: #17b978;">🧪 MLflow Runs</span> ➔
        <span style="color: #17b978;">📦 Artefacts</span> ➔
        <span style="color: #17b978;">👑 Production</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. CONTENU : STRATÉGIE DE CIBLE (Anti-Data Leakage)
st.subheader("1. Protocole expérimental & Target Engineering")
col_split, col_bayes = st.columns([1.1, 0.9])

with col_split:
    with st.container(border=True):
        st.markdown("**🛡️ Isolation stricte (Anti-Data Leakage)**")
        st.write("• **Volume :** 4,48M de transactions (34 variables).")
        st.write("• **Train Set (80%) :** 3,58M dédiés à l'apprentissage.")
        st.write("• **Test Set (20%) :** 895k isolés pour validation.")
        st.success("✔️ Les prix de référence sont calculés exclusivement sur le bloc Train.")

with col_bayes:
    with st.container(border=True):
        st.markdown("**📈 Lissage Bayésien des encadrements spatiaux**")
        st.latex(r"P_{\text{lissé}} = \frac{N_{\text{commune}} \cdot P_{\text{commune}} + K \cdot P_{\text{département}}}{N_{\text{commune}} + K}")
        st.caption("Stabilisation des communes à faible historique de transactions.")

# 6. LES TROIS PILIERS MLOPS
st.markdown("---")
st.subheader("2. Automatisation & Gouvernance")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ✈️ Airflow")
    st.markdown("- **Automatisation** des tâches\n- **Planification** des réentraînements\n- **Orchestration** du DAG complet")

with col2:
    st.markdown("### 📦 DVC")
    st.markdown("- **Versioning** des datasets\n- **Versioning** des modèles\n- **Reproductibilité** garantie")

with col3:
    st.markdown("### 🧪 MLflow")
    st.markdown("- **Tracking** d'expériences\n- **Hyperparamètres** optimisés\n- **Model Registry**")

# 7. CONCLUSION
st.markdown("---")
st.success("""
### 🎯 Garantie de reproductibilité
"Chaque modèle est entièrement reproductible, depuis le dataset source (DVC) jusqu'aux performances obtenues, garantissant une auditabilité totale du cycle de vie."
""")

st.info("👉 **Prochaine étape :** Mise en production avec **Déploiement & Inférence**.")