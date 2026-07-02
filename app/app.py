"""
Compagnon Immobilier — Application principale
Point d'entrée Streamlit : redirige vers la page Estimation par défaut.
"""
import streamlit as st

st.set_page_config(
    page_title="Compagnon Immobilier",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏡 Compagnon Immobilier")

st.markdown("""
Bienvenue dans notre projet d'estimation immobilière.

### Fonctionnalités
- 📊 Exploration des données
- 🧹 Préprocessing
- 🤖 Modélisation
- 🏡 Estimation de prix
- 📈 Évolution du marché
- 🏘️ Comparaison de communes
- 🗺️ Carte nationale
""")


# Redirection vers la page d'accueil
st.switch_page("pages/0_📖_Présentation_Projet.py")
