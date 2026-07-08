import streamlit as st
import os
import streamlit.components.v1 as components

# 1. Configuration et chargement du thème graphique commun
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE, "assets", "style.css")

# Sécurité si le fichier CSS n'existe pas encore dans ce sous-dossier
if os.path.exists(CSS_FILE):
    with open(CSS_FILE, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- INJECTION DE STYLES SUPPLÉMENTAIRES POUR LES EFFETS AVANCÉS ---
st.markdown("""
<style>
    /* Effet de survol sur les cartes (containers) */
    div[data-testid="stVerticalBlockBorderWithLabel"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWithLabel"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }
    /* Style pour la timeline */
    .timeline-step {
        text-align: center;
        padding: 15px;
        background-color: rgba(250, 250, 250, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.05);
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. HERO SECTION (Haut de page)
# ==========================================

components.html(
    """
    <div style="
        background: linear-gradient(135deg, #111e2e 0%, #1f4068 100%);
        padding: 45px 40px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 30px;
        font-family: Arial, sans-serif;
        box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    ">

        <div style="
            color: #ffffff;
            margin: 0;
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: 0.5px;
        ">
            🏡 Compagnon Immobilier MLOps
        </div>

        <div style="
            color: #00eaaf;
            margin-top: 15px;
            font-size: 1.3rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        ">
            Industrialisation d'un pipeline d'intelligence territoriale et d'estimation immobilière
        </div>

        <div style="
            margin-top: 18px;
            width: 55%;
            height: 1px;
            background: rgba(255,255,255,0.35);
            margin-left: auto;
            margin-right: auto;
        "></div>

        <div style="
            margin-top: 18px;
            color: #ffffff;
            font-size: 1.2rem;
            font-style: italic;
            font-weight: 600;
            letter-spacing: 0.4px;
        ">
            De la donnée brute au monitoring en production.
        </div>

    </div>
    """,
    height=250
)

# ==========================================
# 2. LE PROBLÈME MÉTIER
# ==========================================
st.markdown("## 🎯 Le Problème Métier")

with st.container(border=True):
    st.markdown("<h3 style='text-align: center; margin-bottom: 25px;'>Pourquoi deux biens identiques n'ont-ils pas la même valeur ?</h3>", unsafe_allow_html=True)
    
    col_bienA, col_vs, col_bienB = st.columns([4, 2, 4])
    
    with col_bienA:
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.02); padding: 20px; border-radius: 8px; border-left: 5px solid #EF4444; text-align: center;">
            <span style="font-size: 3rem;">🏠</span>
            <h4>Bien A</h4>
            <p>📐 <b>100 m²</b><br>🚪 <b>4 pièces</b><br>
            <hr>
            <h3 style="color: #EF4444; margin: 0;">180 000 €</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with col_vs:
        st.markdown("""
        <div style="text-align: center; padding-top: 40px;">
            <span style="font-size: 2.5rem; font-weight: bold; color: #9CA3AF;">VS</span>
            <br><br>
            <span style="font-size: 2rem;">❓</span>
            <b style="display:block; margin-top:5px;"><br> Écoles, Transports, Richesse, Niveau de vie, DPE...</p>>
        </div>
        """, unsafe_allow_html=True)
        
    with col_bienB:
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.02); padding: 20px; border-radius: 8px; border-left: 5px solid #10B981; text-align: center;">
            <span style="font-size: 3rem;">🏠</span>
            <h4>Bien B</h4>
            <p>📐 <b>100 m²</b><br>🚪 <b>4 pièces</b>
            <hr>
            <h3 style="color: #10B981; margin: 0;">420 000 €</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 25px; padding: 10px; background-color: #EFF6FF; border-radius: 8px;">
        <p style="font-size: 1.1rem; color: #1E40AF; margin: 0; font-weight: 500;">
            💡 <b>Ce qui n'était qu'une interrogation est devenu un modèle prédictif 
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 3. LES CHIFFRES CLÉS (KPI UPDATE)
# ==========================================
st.markdown("## 📊 L'écosystème en Chiffres")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Transactions DVF", value="20 M+")
with kpi2:
    st.metric(label="Sources de données", value="7")
with kpi3:
    st.metric(label="Modèle Core", value="XGBoost Unifié")
with kpi4:
    st.metric(label="Architecture", value="10 Microservices") # nombre de microservices à mettre à jour selon l'architecture finale

st.write("---")


# ==========================================
# 4. LES DEUX AXES DU PROJET
# ==========================================
st.markdown("## 🚀 Produit et Infrastructure")

col1, col2 = st.columns(2)

# COLONNE 1 : LE PRODUIT DATA
with col1:
    with st.container(border=True):
        st.markdown("### 📊 Le Produit Data (Data Science)")
        st.caption("Transformer des millions de données en une estimation immobilière fiable.")
        
        st.markdown("""
        - 🔎 **Préparer les données :** Nettoyage, contrôle qualité et consolidation de plus de 20M de transactions DVF.
        - 🧩 **Enrichir l'information :** Croisement avec DPE, Filosofi, BPE, Sécurité, SNCF pour décrire l'environnement.
        - ⚙️ **Construire les variables métier :** Création de features pertinentes pour capturer les facteurs de valeur.
        - 🤖 **Apprendre à estimer :** Entraînement et optimisation d'un modèle XGBoost unifié.
        """)
        
        st.success("**🎯 Objectif :** Fournir une estimation précise, robuste et explicable.")

# COLONNE 2 : L'INFRASTRUCTURE MLOPS
with col2:
    with st.container(border=True):
        st.markdown("### 🏗️ Produit & Infrastructure (MLOps)")
        st.caption("Transformer un modèle performant en un produit fiable et reproductible.")
        
        st.markdown("""
        - 📦 **Conteneurisation :** Isolation avec Docker Compose pour garantir la portabilité.
        - 🔄 **Pipelines automatisés :** Orchestration des traitements et déploiements avec Airflow.
        - 📚 **Versioning & Traçabilité :** Suivi des données (DVC) et des expérimentations (MLflow).
        - 📈 **Déploiement & Monitoring :** Microservices dédiés, suivi des perfs et supervision.
        """)
        
        st.info("**🎯 Objectif :** Garantir un pipeline reproductible et un service disponible en continu.")

# ==========================================
# 6. TRANSITION FINALE
# ==========================================
st.markdown("""
<div style="background-color: #111827; color: white; padding: 30px; border-radius: 8px; border-left: 6px solid #3B82F6; margin-top: 20px;">
    <div style="color:#FFFFFF !important; font-size: 1.3rem; font-weight: 700; margin-top: 0; margin-bottom: 10px;">
        De la donnée brute à la mise en production : un cycle de vie complet maîtrisé par notre approche MLOps.
    </div>
    </p>
</div>
""", unsafe_allow_html=True)