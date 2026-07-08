import streamlit as st

st.set_page_config(page_title="Déploiement & Inférence", layout="wide")

st.title("🚀 Déploiement & Inférence")

st.markdown("""
Le modèle est entraîné, les résultats sont bons.
Maintenant, il faut le **mettre à disposition** pour que les utilisateurs puissent l'utiliser.
""")

st.markdown("---")

st.header("1. FastAPI : l'interface du modèle")

st.markdown("""
On a créé une **API** avec FastAPI. Une API, c'est comme un service web :
on lui envoie des informations (surface, département, type de bien...),
et elle nous répond avec le prix estimé.

L'avantage : n'importe quel outil peut appeler cette API — notre Streamlit,
un site web, une application mobile, etc.
""")

st.markdown("**Nos endpoints :**")
col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("**POST /predict**")
        st.markdown("Reçoit les caractéristiques d'un bien et retourne le prix estimé en €/m²")
with col2:
    with st.container(border=True):
        st.markdown("**GET /health**")
        st.markdown("Vérifie que l'API fonctionne et que le modèle est chargé")
with col3:
    with st.container(border=True):
        st.markdown("**GET /model/info**")
        st.markdown("Affiche la version du modèle en production et ses métriques")

st.markdown("---")

st.header("2. Comment fonctionne une prédiction ?")

st.markdown("Voici ce qui se passe quand on clique sur 'Estimer' dans la page Estimation :")

st.code("""
1. Streamlit envoie les données du formulaire à FastAPI (POST /predict)
   → surface, nb pièces, type de bien, département...

2. FastAPI valide les données avec Pydantic
   → vérifie que la surface est > 0, que le type est "appart" ou "maison", etc.

3. FastAPI construit le vecteur de 31 variables
   → ajoute les prix moyens de la commune, les statistiques socio-économiques...

4. XGBoost prédit le résiduel
   → le résiduel = écart entre ce bien et la moyenne de sa commune

5. FastAPI calcule le prix final
   → prix/m² = résiduel + prix moyen de la commune

6. FastAPI répond avec le résultat en JSON
   → { "prediction_eur_m2": 4200, "prediction_total_eur": 294000, ... }

7. Streamlit affiche le résultat à l'utilisateur
""", language="")

st.markdown("---")

st.header("3. Nginx : la sécurité devant l'API")

st.markdown("""
On n'expose pas FastAPI directement sur internet. On passe par **Nginx** qui :
- Force le **HTTPS** (connexion chiffrée)
- Limite à **10 requêtes par seconde** par IP (pour éviter les abus)
- Bloque l'accès aux métriques de l'extérieur (Prometheus ne doit pas être public)
""")

st.code("""
Utilisateur → HTTPS port 443 → Nginx → FastAPI port 8000 → XGBoost
""", language="")

st.markdown("---")

st.header("4. Le modèle en production")

st.markdown("""
FastAPI charge le modèle au démarrage depuis **MLflow** avec l'alias "production".
Si on entraîne un nouveau modèle et qu'on le met en production dans MLflow,
l'API le prend au prochain redémarrage — sans toucher au code.
""")

col1, col2 = st.columns(2)
with col1:
    st.metric("Modèle en production", "compagnon-immobilier v1")
    st.metric("MAE", "648 €/m²")
with col2:
    st.metric("R²", "0.80")
    st.metric("Variables utilisées", "31")

st.success("✅ La documentation Swagger est disponible automatiquement sur **/docs** — pas besoin de la créer manuellement, FastAPI la génère seule.")
