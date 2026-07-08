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
- 📖_Présentation_Projet
- 🤖_De la donnée brute à la donnée prédictive
- 🏗️ Architecture Globale
- 🐳 Infrastructure & Microservices
- ⚙️ Pipeline d'entraînement & Gouvernance
- 🚀 Déploiement & Inférence
- 📈 Monitoring & Cycle de vie
- 🔍_Estimation       
""")


# Redirection vers la page d'accueil
st.switch_page("pages/0_📖_Présentation_Projet.py")
