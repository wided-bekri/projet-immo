import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Pipeline & Gouvernance", layout="wide")

st.title("⚙️ Pipeline d'entraînement & Gouvernance")

st.markdown("""
Cette page explique comment on a **entraîné notre modèle** et comment on **garde une trace de tout**
pour pouvoir reproduire les résultats à tout moment.
""")

st.markdown("---")

st.header("1. Les données d'entraînement")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Ce qu'on a utilisé")
    st.markdown("""
    - **4,48 millions** de transactions immobilières (fichier DVF)
    - Données de 2022 à 2025
    - **31 variables** par transaction : surface, nombre de pièces, département, prix moyen de la commune, etc.
    """)

with col2:
    st.markdown("### Comment on a découpé")
    st.markdown("""
    - **80% pour entraîner** le modèle → 3,58 millions de transactions
    - **20% pour tester** les résultats → 895 000 transactions

    Le modèle n'a jamais vu les données de test pendant l'entraînement.
    C'est comme réviser avec un livre, puis passer un examen avec des nouvelles questions.
    """)

st.markdown("---")

st.header("2. L'entraînement avec XGBoost")

st.markdown("""
On a choisi **XGBoost** parce que c'est un algorithme qui gère bien les données tabulaires
(lignes et colonnes) et qui est rapide à entraîner même sur des millions de lignes.

XGBoost construit des centaines d'arbres de décision les uns après les autres.
Chaque arbre corrige les erreurs du précédent.

On a fait le choix de garder **un seul modèle XGBoost** entraîné sur l'ensemble des données françaises.
Un modèle unique, simple et robuste — capable de gérer toute la diversité du marché immobilier français.
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions analysées", "4,48M")
col2.metric("MAE (erreur moyenne)", "648 €/m²")
col3.metric("R² (précision globale)", "0.80")
col4.metric("Arbres XGBoost", "800")

st.markdown("**Hyperparamètres du modèle final :** `n_estimators=800` · `max_depth=8` · `learning_rate=0.05`")

st.info("💡 **R² = 0.80** signifie que le modèle explique 80% des variations de prix. C'est correct pour un marché aussi complexe que l'immobilier français.")

st.markdown("---")

st.header("3. MLflow : notre journal de bord")

st.markdown("""
**Problème :** si on entraîne 10 versions du modèle avec des paramètres différents,
comment on sait laquelle était la meilleure 3 semaines plus tard ?

**Solution : MLflow.** À chaque entraînement, MLflow enregistre automatiquement :
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**📊 Les métriques**")
    st.markdown("MAE, R², RMSE — pour comparer les versions")
with col2:
    st.markdown("**⚙️ Les paramètres**")
    st.markdown("n_estimators, max_depth, learning_rate — pour reproduire le modèle")
with col3:
    st.markdown("**📦 Le modèle**")
    st.markdown("Le fichier du modèle entraîné — pour le réutiliser en production")

st.markdown("---")

# Intégration des images MLflow
st.subheader("Visualisation de l'historique des Runs")

try:
    st.image("app/images/mlflow_runs.png", caption="Liste de tous les runs MLflow — chaque ligne = un entraînement", use_container_width=True)
except FileNotFoundError:
    st.warning("mlflow_runs.png introuvable.")

try:
    st.image("app/images/mlflow_run_detail.png", caption="Détail d'un run : paramètres et métriques enregistrés", use_container_width=True)
except FileNotFoundError:
    st.warning("mlflow_run_detail.png introuvable.")

try:
    st.image("app/images/mlflow_version5.png", caption="Modèle v5 enregistré dans le Registry avec alias 'production'", use_container_width=True)
except FileNotFoundError:
    st.warning("mlflow_version5.png introuvable.")

# Lien d'accès direct
MLFLOW_URL = os.environ.get("MLFLOW_URL", "http://localhost:5000")
st.markdown(f"""
**Accès MLflow :** [Cliquez ici pour accéder au Dashboard MLflow]({MLFLOW_URL})  
*Enregistrez vos expériences pour garantir la reproductibilité totale.*
""")
st.markdown("---")

st.header("4. Le Model Registry et l'alias 'production'")

try:
    st.image("app/images/mlflow_registry.png", caption="MLflow Model Registry — compagnon-immobilier avec alias @production", use_container_width=True)
except FileNotFoundError:
    st.warning("mlflow_registry.png introuvable.")

st.markdown("""
Une fois qu'un modèle est validé, on lui donne l'alias **"production"** dans MLflow.

FastAPI charge **toujours le modèle avec l'alias "production"**.
Si on entraîne un meilleur modèle et qu'on change l'alias, FastAPI le prend automatiquement
**sans avoir à modifier le code**.
""")

st.code("""
# Ce que fait FastAPI au démarrage
model = mlflow.load_model(alias="production")
""", language="python")

st.markdown("---")

st.header("5. DVC : versioning des données")

st.markdown("""
Les fichiers de données font plusieurs Go — trop gros pour Git.
**DVC** (Data Version Control) stocke les données sur DagsHub et garde dans Git
uniquement un petit fichier pointeur qui dit "les données sont là-bas".

Ainsi, n'importe qui peut récupérer exactement les mêmes données qu'on a utilisées.
""")

st.success("✅ Résultat : si quelqu'un veut reproduire notre modèle dans 6 mois, il peut récupérer les mêmes données (DVC) et voir tous les paramètres d'entraînement (MLflow).")
