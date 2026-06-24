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

# Redirection vers la page d'accueil
st.switch_page("pages/4_🔍_Estimation.py")



