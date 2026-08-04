import streamlit as st

st.set_page_config(page_title="Déploiement & Inférence", layout="wide")

st.title("🚀 Déploiement & Inférence")

st.markdown("""
Le modèle est entraîné, les résultats sont bons.
Maintenant il faut le **mettre à disposition** pour que n'importe qui puisse l'utiliser —
pas juste nous, mais aussi un site web, une application mobile, ou un autre service.
""")

st.markdown("---")

st.success("""
✅ **Ce qu'on a mis en place :**
- Une API FastAPI pour recevoir les demandes de prédiction
- Nginx devant l'API pour la sécurité et le HTTPS
- Le modèle chargé automatiquement depuis MLflow au démarrage
""")

st.markdown("---")

st.header("1. FastAPI : l'interface du modèle")

st.markdown("""
**FastAPI** est le pont entre l'utilisateur et le modèle XGBoost.

On lui envoie les caractéristiques d'un bien (surface, département, type de bien...),
et il nous répond avec le **prix estimé en €/m²**.

L'avantage : n'importe quel outil peut appeler cette API — notre Streamlit,
un site web, une application mobile, etc.
""")

st.markdown("**Nos 3 endpoints :**")

col1, col2, col3 = st.columns(3)
with col1:
    with st.container(border=True):
        st.markdown("### POST /predict")
        st.markdown("Reçoit les caractéristiques d'un bien et retourne le prix estimé en €/m²")
with col2:
    with st.container(border=True):
        st.markdown("### GET /health")
        st.markdown("Vérifie que l'API fonctionne et que le modèle est bien chargé")
with col3:
    with st.container(border=True):
        st.markdown("### GET /model/info")
        st.markdown("Affiche la version du modèle en production et ses métriques (MAE, R²)")

try:
    st.image("app/images/endpoints_docs.png", caption="Interface Swagger — documentation interactive de l'API FastAPI", use_container_width=True)
except FileNotFoundError:
    st.warning("endpoints_docs.png introuvable.")

st.markdown("---")

st.header("2. Comment fonctionne une prédiction ?")

st.markdown("Voici ce qui se passe quand on clique sur **Estimer** dans la page Estimation :")

st.code("""
1. Streamlit envoie les données du formulaire à FastAPI (POST /predict)
   → surface, nb pièces, type de bien, département...

2. FastAPI valide les données avec Pydantic
   → vérifie que la surface est > 0, que le type est correct, etc.

3. FastAPI construit le vecteur de 31 variables
   → ajoute les prix moyens de la commune, les statistiques socio-économiques...

4. XGBoost prédit le résiduel
   → le résiduel = écart entre ce bien et la moyenne de sa commune

5. FastAPI calcule le prix final
   → prix/m² = résiduel + prix moyen de la commune

6. FastAPI répond avec le résultat en JSON
   → { "prediction_eur_m2": 4200, "prediction_total_eur": 294000 }

7. Streamlit affiche le résultat à l'utilisateur
""", language="")

st.markdown("---")

st.header("3. Nginx : la protection devant l'API")

st.markdown("""
On n'expose pas FastAPI directement sur internet.
On place **Nginx** devant comme un gardien qui :
- Force le **HTTPS** → la connexion est chiffrée, les données sont protégées
- Limite à **10 requêtes par seconde** par IP → évite les abus et les attaques
- Bloque l'accès aux métriques internes → Prometheus n'est pas accessible depuis l'extérieur
""")

st.code("""
Utilisateur → HTTPS (port 443) → Nginx → FastAPI (port 8000) → XGBoost → Résultat
""", language="")

st.markdown("---")

st.header("4. Le modèle en production")

st.markdown("""
FastAPI charge le modèle **automatiquement au démarrage** depuis MLflow avec l'alias **"production"**.

Si on entraîne un meilleur modèle et qu'on change l'alias dans MLflow,
l'API le prend au prochain redémarrage — **sans toucher au code**.
""")

col1, col2 = st.columns(2)
with col1:
    st.metric("Modèle en production", "compagnon-immobilier v5")
    st.metric("MAE (erreur moyenne)", "648 €/m²")
with col2:
    st.metric("R² (précision globale)", "0.80")
    st.metric("Variables utilisées", "31")

st.markdown("---")

st.header("5. Sécurité : ce qu'on a et ce qu'on prévoit")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**✅ Ce qu'on a déjà (Phase 1) :**")
    st.markdown("""
- **HTTPS** via Nginx (connexion chiffrée)
- **Rate limiting** : 10 requêtes/seconde max par IP
- **Isolation réseau** : l'API passe obligatoirement par Nginx
- **Métriques privées** : `/metrics` accessible uniquement en interne
    """)
with col2:
    st.markdown("**✅ Sécurité supplémentaire déjà en place :**")
    st.markdown("""
- **API Key** (`X-API-Key`) : chaque appel à `/predict` doit inclure un token secret
- **401 Unauthorized** : retourné automatiquement si la clé est absente ou invalide
- **🔜 Améliorations futures :** gestion des rôles, audit log, blacklist d'IP
    """)
