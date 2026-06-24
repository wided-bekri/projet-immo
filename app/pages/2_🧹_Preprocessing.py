import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==================================================
# Style commun
# ==================================================

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS_FILE = os.path.join(BASE, "assets", "style.css")

with open(CSS_FILE, encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# ==================================================
# SECTION 0 — BANDEAU D'INTRODUCTION
# ==================================================
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #1e3d59 0%, #17b978 100%); padding: 40px; border-radius: 12px; margin-bottom: 30px; color: white; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🛠️ Phase II — Préparation et enrichissement des données</h1>
        <p style="font-size: 1.2rem; opacity: 0.95; margin-top: 15px; margin-bottom: 25px; max-width: 900px; margin-left: auto; margin-right: auto;">
            Transformer plus de 20 millions de transactions immobilières en un dataset fiable, enrichi et compatible avec une utilisation industrielle du Machine Learning.
        </p>
        <div style="display: flex; justify-content: center; align-items: center; gap: 15px; font-weight: bold; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 8px; font-size: 0.9rem;">
            <span>📦 Données Brutes</span> ➔ <span>🧹 Nettoyage</span> ➔ <span>🌍 Enrichissement</span> ➔ <span>⚙️ Feature Engineering</span> ➔ <span>🤖 Machine Learning</span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==================================================
# SECTION 1 — KPI DU PIPELINE
# ==================================================
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    with st.container(border=True):
        st.metric(label="🏠 Transactions DVF initiales", value="20,1 M")
with kpi_col2:
    with st.container(border=True):
        st.metric(label="🤖 Dataset final", value="4,48 M")
with kpi_col3:
    with st.container(border=True):
        st.metric(label="🌍 Sources fusionnées", value="7")
with kpi_col4:
    with st.container(border=True):
        st.metric(label="📊 Variables finales", value="34")

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# SECTION 2 — L'ENTONNOIR DE TRANSFORMATION
# ==================================================
st.header("2. L'entonnoir de transformation")

col_funnel, col_funnel_info = st.columns([2, 1])

with col_funnel:
    # Génération du Funnel Plot de Plotly
    funnel_data = dict(
        number=[20100000, 12500000, 8100000, 5200000, 4480000],
        stage=["Transactions DVF Brutes", "Biens Résidentiels", "Suppression Incohérences", "Suppression Outliers", "Fusion Multi-sources (Final)"]
    )
    fig_funnel = px.funnel(
        funnel_data, x='number', y='stage',
        color_discrete_sequence=px.colors.sequential.YlGnBu_r
    )
    fig_funnel.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=350)
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_funnel_info:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("💡 Pourquoi filtrer ?")
        st.markdown(
            """
            * **✓ Erreurs de saisie :** Prix aberrants ou inversions de surfaces.
            * **✓ Transactions atypiques :** Ventes de châteaux, locaux commerciaux, forêts.
            * **✓ Parcelles non résidentielles :** Terrains nus ou agricoles vendus seuls.
            * **✓ Valeurs impossibles :** Déclarant des surfaces à 0 m² ou des prix < 500€.
            """
        )

st.markdown("---")

# ==================================================
# SECTION 3 — ARCHITECTURE D'ENRICHISSEMENT
# ==================================================
st.header("🌍 Construction d'un écosystème de données territoriales")

# Schéma d'architecture en HTML/CSS pour éviter le rendu Excel
st.markdown(
    """
    <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 25px; text-align: center; margin-bottom: 25px;">
        <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;">
            <div style="background: #1e3d59; padding: 12px; border-radius: 6px; min-width: 100px;">🏠<br><b>DVF</b></div>
            <div style="background: rgba(128,128,128,0.2); padding: 12px; border-radius: 6px; min-width: 100px;">👥<br><b>Population</b></div>
            <div style="background: rgba(128,128,128,0.2); padding: 12px; border-radius: 6px; min-width: 100px;">💰<br><b>Filosofi</b></div>
            <div style="background: rgba(128,128,128,0.2); padding: 12px; border-radius: 6px; min-width: 100px;">🏪<br><b>BPE</b></div>
            <div style="background: rgba(128,128,128,0.2); padding: 12px; border-radius: 6px; min-width: 100px;">🚔<br><b>Criminalité</b></div>
            <div style="background: rgba(128,128,128,0.2); padding: 12px; border-radius: 6px; min-width: 100px;">⚡<br><b>DPE</b></div>
            <div style="background: rgba(128,128,128,0.2); padding: 12px; border-radius: 6px; min-width: 100px;">🚉<br><b>SNCF</b></div>
        </div>
        <div style="font-size: 1.5rem; margin-bottom: 15px;">⬇️</div>
        <div style="background: #17b978; color: white; display: inline-block; padding: 10px 30px; border-radius: 20px; font-weight: bold; margin-bottom: 10px;">⚡ 68 Variables enrichies calculées</div>
        <div style="font-size: 1.5rem; margin-bottom: 10px;">⬇️</div>
        <div style="border: 2px dashed #17b978; display: inline-block; padding: 10px 40px; border-radius: 8px; font-weight: bold; letter-spacing: 1px;">💎 DATASET CONSOLIDÉ</div>
    </div>
    """, 
    unsafe_allow_html=True
)

# 7 Cartes horizontales condensées pour détailler les sources
src_cols = st.columns(7)
src_details = [
    {"icon": "🏠 DVF", "text": "20 M transactions"},
    {"icon": "👥 Pop.", "text": "Dynamique démo."},
    {"icon": "💰 Filosofi", "text": "Revenus / Pauvreté"},
    {"icon": "🏪 BPE", "text": "7 types d'équip."},
    {"icon": "🚔 Sécu", "text": "17 indicateurs"},
    {"icon": "⚡ DPE", "text": "Performance éner."},
    {"icon": "🚉 SNCF", "text": "Accessibilité"}
]
for idx, item in enumerate(src_details):
    with src_cols[idx]:
        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(128,128,128,0.15); padding: 10px; border-radius: 6px; text-align: center; height: 100%;">
                <div style="font-weight: bold; font-size: 0.9rem; color: #17b978;">{item['icon']}</div>
                <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 5px;">{item['text']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

st.markdown("---")

# ==================================================
# SECTION 4 — NETTOYAGE MÉTIER
# ==================================================
st.header("🧹 Élimination des incohérences")

col_table, col_alert_net = st.columns([2, 1])

with col_table:
    rules_df = pd.DataFrame({
        "Variable": ["Surface bâtie", "Surface par pièce", "Terrain", "Valeur foncière", "Prix au m²"],
        "Règle appliquée": ["10 à 500 m²", "7 à 80 m²", "< 10 000 m²", "20 k€ à 2 M€", "300 € à 15 000 €"]
    })
    st.table(rules_df)

with col_alert_net:
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ Ces seuils proviennent directement des anomalies réelles observées lors de la phase d'analyse exploratoire (EDA).")

st.markdown("---")

# ==================================================
# SECTION 5 — FEATURE ENGINEERING
# ==================================================
st.header("⚙️ Création des variables métier")

fe1, fe2, fe3, fe4 = st.columns(4)

with fe1:
    with st.container(border=True):
        st.markdown("#### 🏠 Bien")
        st.caption("- `surface_par_piece` \n- `is_maison` \n- `age_construction`")
with fe2:
    with st.container(border=True):
        st.markdown("#### 🌍 Territoire")
        st.caption("- `revenu_median` \n- `evolution_pop_10_ans` \n- `transports_pour_1000`")
with fe3:
    with st.container(border=True):
        st.markdown("#### ⚡ Énergie")
        st.caption("- `target_dpe_num` \n- `cout_total_5_usages` \n- `has_dpe`")
with fe4:
    with st.container(border=True):
        st.markdown("#### 📍 Géographie")
        st.caption("- `latitude` \n- `longitude` \n- `is_metropole`")

# Exemple visuel de transformation
st.markdown(
    """
    <div style="background-color: rgba(23, 185, 120, 0.05); border: 1px dashed #17b978; padding: 15px; border-radius: 8px; text-align: center; margin-top: 15px; font-weight: bold;">
        💡 Exemple : Surface = 120 m² & Pièces = 5 ➔ <code>surface_par_piece</code> = 24 m²
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("---")

# ==================================================
# SECTION 6 — GESTION DES DONNÉES MANQUANTES
# ==================================================
st.header("🩹 Gestion intelligente des valeurs manquantes")

col_na_main, col_na_side = st.columns([2, 1])

with col_na_main:
    na_df = pd.DataFrame({
        "Source": ["Population", "Revenus", "Équipements", "Criminalité", "DPE"],
        "Traitement appliqué": ["Médiane communale", "Médiane départementale", "Remplacement par 0 (Absence)", "Remplacement par 0 (Absence)", "Conservation stratégique + Indicateurs Boolean"]
    })
    st.dataframe(na_df, use_container_width=True, hide_index=True)

with col_na_side:
    with st.container(border=True):
        st.markdown("#### ⚡ Focus Encodage DPE")
        
        # Petit tableau des scores DPE
        dpe_score_df = pd.DataFrame({
            "DPE": ["A", "B", "C", "D", "E", "F", "G"],
            "Score": [7, 6, 5, 4, 3, 2, 1]
        })
        st.dataframe(dpe_score_df, use_container_width=True, hide_index=True, height=140)
        
        st.markdown("**Variables créées :**\n* ✓ `has_dpe`\n* ✓ `has_cout_usages`")
        
        st.caption("ℹ️ *Plus de 3,1 millions de diagnostics énergétiques manquants compensés par indicateurs.*")

st.markdown("---")

# ==================================================
# SECTION 7 — 🛡️ PRÉVENTION DU DATA LEAKAGE & ML
# ==================================================
st.header("🛡️ Prévention du Data Leakage & Construction ML")

col_leak, col_bayes = st.columns(2)

with col_leak:
    st.subheader("Protocole de Validation Split")
    
    # Séparation visuelle Bonne/Mauvaise pratique
    bad_col, good_col = st.columns(2)
    with bad_col:
        st.markdown(
            """
            <div style="border: 1px solid #FF4B4B; padding: 12px; border-radius: 6px; background: rgba(255,75,75,0.05); height: 100%;">
                <h5 style="color: #FF4B4B; margin: 0;">❌ Mauvaise Pratique</h5>
                <p style="font-size: 0.8rem; margin-top: 5px;">Dataset complet ➔ Calcul stats globales ➔ Split Train/Test</p>
                <b style="font-size: 0.8rem; color: #FF4B4B;">Resultat : Fuite de données (Data Leakage)</b>
            </div>
            """, unsafe_allow_html=True
        )
    with good_col:
        st.markdown(
            """
            <div style="border: 1px solid #17b978; padding: 12px; border-radius: 6px; background: rgba(23,185,120,0.05); height: 100%;">
                <h5 style="color: #17b978; margin: 0;">✔ Protocole Industriel</h5>
                <p style="font-size: 0.8rem; margin-top: 5px;">Split Train/Test d'abord ➔ Calcul stats uniquement sur TRAIN ➔ Mapping sur TEST</p>
            </div>
            """, unsafe_allow_html=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Variables de marché créées uniquement sur le Train :**")
    st.caption("✓ Prix médian communal • ✓ Prix médian départemental • ✓ Volumes • ✓ Prix par type")

with col_bayes:
    st.subheader("Lissage Bayésien des prix médians")
    
    # Explication de la fiabilité
    b_c1, b_c2 = st.columns(2)
    b_c1.metric(label="📍 Commune A (Faible volume)", value="3 ventes", delta="Peu fiable", delta_color="inverse")
    b_c2.metric(label="📍 Commune B (Fort volume)", value="8 000 ventes", delta="Fiable", delta_color="normal")
    
    st.markdown("Pour éviter la volatilité statistique des petites communes, on applique la formule :")
    st.latex(r"Prix_{lisse} = \frac{Prix_{local} \times Volume + Prix_{dept} \times k}{Volume + k}")
    st.caption("Fixé à $k = 15$ d'après nos tests empiriques.")

# Encadré final de ciblage du modèle (Plein écran sous le layout 2 colonnes)
st.markdown("<br>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown(
        r"""
        <div style="text-align: center;">
            <h4 style="margin: 0; color: #1e3d59;">🎯 Cible finale du modèle de Machine Learning</h4>
            <p style="font-size: 1.1rem; font-weight: bold; margin: 10px 0;">
                Résiduel = Prix réel au m² − Prix médian communal (du type de bien)
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.markdown(
        """
        En prédisant le résiduel, l'algorithme n'apprend pas bêtement le niveau général des prix de la commune, 
        mais **se focalise sur la qualité intrinsèque du bien**, son micro-environnement immédiat, sa performance énergétique et ses caractéristiques propres.
        """
    )

# ==================================================
# CONCLUSION & TRANSITION
# ==================================================
st.markdown("<br>", unsafe_allow_html=True)
st.divider()
with st.container(border=True):
    st.markdown("### ✨ Bilan : Le Dataset est prêt")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("* **✓ 4,48 millions** de transactions parfaitement exploitables.")
        st.markdown("* **✓ 34 variables explicatives** nettoyées et scalées.")
        st.markdown("* **✓ 7 sources de données** interconnectées de manière fluide.")
    with cc2:
        st.markdown("* **✓ Gestion robuste** des valeurs manquantes sans perte d'information.")
        st.markdown("* **✓ Enrichissement territorial** massif pour capter le contexte.")
        st.markdown("* **✓ Risque de Data Leakage éliminé** à 100% via nos pipelines Scikit-Learn.")
