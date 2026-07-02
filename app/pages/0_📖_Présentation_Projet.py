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
            De la donnée brute au monitoring en production : un projet d'infrastructure de bout en bout.
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
            <h4>Bien Enclavé</h4>
            <p>📐 <b>100 m²</b><br>🚪 <b>4 pièces</b><br>⚠️ Niveau de vie bas</p>
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
            <b style="display:block; margin-top:5px;">L'impact territorial</b>
        </div>
        """, unsafe_allow_html=True)
        
    with col_bienB:
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.02); padding: 20px; border-radius: 8px; border-left: 5px solid #10B981; text-align: center;">
            <span style="font-size: 3rem;">🏠</span>
            <h4>Bien Connecté</h4>
            <p>📐 <b>100 m²</b><br>🚪 <b>4 pièces</b><br>✅ Écoles, Transports, Richesse</p>
            <hr>
            <h3 style="color: #10B981; margin: 0;">420 000 €</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 25px; padding: 10px; background-color: #EFF6FF; border-radius: 8px;">
        <p style="font-size: 1.1rem; color: #1E40AF; margin: 0; font-weight: 500;">
            💡 <b>Défi :</b> Capturer la richesse des données publiques (INSEE, DVF, DPE) pour fournir une estimation hautement fiable via une API résiliente.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 3. LES DEUX AXES DU PROJET
# ==========================================
st.markdown("## ⚔️ Vision Produit vs Vision Infrastructure")

col_axe1, col_axe2 = st.columns(2)

with col_axe1:
    with st.container(border=True):
        st.markdown("### 🗺️ Le Produit Data (Data Science)")
        st.markdown("*Donner du sens aux indicateurs croisés*")
        
        st.markdown("""
        - 📊 **Analyse Exploratoire :** Nettoyage de 20M de lignes DVF.
        - 🧪 **Feature Engineering :** Fusion géographique (Filosofi, BPE, Sécurité).
        - 🤖 **Modèle Prédictif :** Algorithme XGBoost optimisé pour la prédiction de prix au m².
        """)
        
        st.markdown("""
        <div style="background-color: #EEF2F6; padding: 12px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #3B82F6;">
            <b>🎯 Objectif :</b> Précision de l'estimation métrique.
        </div>
        """, unsafe_allow_html=True)

with col_axe2:
    with st.container(border=True):
        st.markdown("### 🏗️ L'Usine Logicielle (MLOps)")
        st.markdown("*Garantir la stabilité, le tracking et le monitoring*")
        
        st.markdown("""
        - 📦 **Conteneurisation :** Isolation complète sous Docker-Compose.
        - 🔄 **Orchestration :** Pipelines automatisés programmés via Airflow.
        - 🛡️ **Gouvernance & Suivi :** Versioning DVC et tracking d'expériences MLflow.
        """)
        
        st.markdown("""
        <div style="background-color: #EEF2F6; padding: 12px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #10B981;">
            <b>🎯 Objectif :</b> Reproductibilité et zéro coupure en production.
        </div>
        """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 4. LES CHIFFRES CLÉS (KPI UPDATE)
# ==========================================
st.markdown("## 📊 L'écosystème en Chiffres")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Transactions DVF", value="20 M+")
with kpi2:
    st.metric(label="Sources de données", value="7")
with kpi3:
    st.metric(label="Modèle Core", value="XGBoost Single")
with kpi4:
    st.metric(label="Architecture", value="10 Microservices")

st.write("---")


# ==========================================
# 5. TIMELINE DU PROJET (Refondue sur les 4 phases de soutenance)
# ==========================================
st.markdown("## ⏳ Feuille de Route de l'Industrialisation (Chronologie de la Présentation)")

t1, t2, t3, t4 = st.columns(4)

with t1:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">📦</span>
        <h4 style="margin: 10px 0 5px 0; color:#3B82F6;">Phase 1</h4>
        <b>Fondations & API</b><br>
        <small style="color:#6B7280;">Baseline XGBoost, tests unitaires et création du service FastAPI initial.</small>
    </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">🔄</span>
        <h4 style="margin: 10px 0 5px 0; color:#F59E0B;">Phase 2</h4>
        <b>Tracking & Data</b><br>
        <small style="color:#6B7280;">Gouvernance complète du code avec MLflow et stockage/versioning des datasets via DVC.</small>
    </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">⛓️</span>
        <h4 style="margin: 10px 0 5px 0; color:#10B981;">Phase 3</h4>
        <b>Orchestration & CI</b><br>
        <small style="color:#6B7280;">Architecture multi-services Docker, automatisation Airflow et pipeline CI/CD.</small>
    </div>
    """, unsafe_allow_html=True)

with t4:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">🛡️</span>
        <h4 style="margin: 10px 0 5px 0; color:#8B5CF6;">Phase 4</h4>
        <b>Monitoring & Drift</b><br>
        <small style="color:#6B7280;">Supervision en direct avec Prometheus/Grafana et calcul de dérive des données avec Evidently.</small>
    </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 6. TRANSITION FINALE
# ==========================================
st.markdown("""
<div style="background-color: #111827; color: white; padding: 30px; border-radius: 8px; border-left: 6px solid #3B82F6; margin-top: 20px;">
    <div style="color:#FFFFFF !important; font-size: 1.3rem; font-weight: 700; margin-top: 0; margin-bottom: 10px;">
        Structure de la soutenance
    </div>
    <p style="margin-bottom: 0; opacity: 0.9; line-height: 1.6; color: #ffffff;">
        Pour explorer les entrailles techniques de cette plateforme, utilisez le menu latéral. Nous débuterons par notre 
        <b>Laboratoire de Data Science</b> pour analyser les données de base, avant de décortiquer pas à pas l'infrastructure 
        <b>MLOps (Tracking, Orchestration et Production)</b> mise en place pour faire tourner l'application de simulation finale.
    </p>
</div>
""", unsafe_allow_html=True)