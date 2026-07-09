import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
try:
    from streamlit_folium import st_folium
    import folium
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# ==================================================
# 1. CONFIGURATION
# ==================================================
st.set_page_config(page_title="Data Science Lab - Compagnon Immobilier", page_icon="🧪", layout="wide")

# Simulation de données pour le portrait-robot
@st.cache_data
def load_mock_data():
    n = 1000
    return pd.DataFrame({
        "surface_reelle_bati": np.random.normal(85, 30, n).clip(15, 300),
        "nombre_pieces_principales": np.random.randint(1, 6, n),
        "valeur_fonciere": np.random.exponential(250000, n).clip(50000, 1000000)
    })

df_raw_viz = load_mock_data()

st.title("🧪 Pipeline de Traitement des Données")

# --- AJOUT DE LA FRISE DE DÉMARCHE ---
st.markdown("""
<div style="
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    background: #f8f9fa; 
    padding: 15px 20px; 
    border-radius: 8px; 
    border: 1px solid #e0e0e0;
    margin-bottom: 30px;
    font-size: 0.85rem;
    font-weight: 600;
">
    <div style="text-align: center;">📊<br>20M DVF</div>
    <div style="color: #ccc;">➔</div>
    <div style="text-align: center;">🔎<br>Préparation</div>
    <div style="color: #ccc;">➔</div>
    <div style="text-align: center;">🧩<br>Enrichissement</div>
    <div style="color: #ccc;">➔</div>
    <div style="text-align: center;">⚙️<br>Feature Eng.</div>
    <div style="color: #ccc;">➔</div>
    <div style="text-align: center;">🤖<br>XGBoost</div>
    <div style="color: #ccc;">➔</div>
    <div style="text-align: center;">💰<br>Estimation</div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 2. CRÉATION DES ONGLETS
# ==================================================
tab1, tab2, tab3, tab4 = st.tabs(["🔎 1. Préparation", "🧩 2. Enrichissement", "⚙️ 3. Fiabilisation", "🤖 4. Modélisation"])

# ==================================================
# CONTENU ONGLET 1
# ==================================================
with tab1:
    st.header("🔎 1. Préparation des données")
    st.markdown("##### *Objectif : Construire un socle de données fiable et intègre.*")

    st.subheader("🚉 Zoom sur la matière première : La base DVF")
    
    # KPIs
    kpi_1, kpi_2, kpi_3 = st.columns(3)
    kpi_1.metric("📊 Volume d'Historique", "+20 M lignes")
    kpi_2.metric("⏳ Amplitude Temporelle", "2020 ➔ S1 2025")
    kpi_3.metric("🌍 Maillage Territorial", "~34 000 communes")

    # Graphique sous KPI 2
    _, col_graph, _ = st.columns([1, 2, 1])
    with col_graph:
        st.subheader("📅 Transactions par année")
        df_years = pd.DataFrame({"Année": [2020, 2021, 2022, 2023, 2024, 2025], "Nb": [1.2, 1.5, 1.4, 1.1, 1.0, 0.6]})
        fig_years = px.bar(df_years, x="Année", y="Nb", color_discrete_sequence=['#ff9f43'])
        fig_years.update_layout(height=250, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_years, use_container_width=True)

    # Entonnoir et Process
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("""
        ### 🛠️ Data Preparation : De la donnée brute à la valeur
        > **Le constat :** Un gisement massif de 20M de transactions brutes, inexploitables en l'état à cause du bruit et des incohérences inhérentes aux registres fonciers.
        
        * **Audit Qualité :** Standardisation des flux DVF.
        * **Filtrage Intelligent :** Focus exclusif sur le résidentiel.
        * **Nettoyage Statistiques :** Détection des valeurs aberrantes.
        
        **🎯 Résultat :** Un dataset "propre", harmonisé et prêt pour l'ingénierie.
        """)
    
    with col_right:
        st.subheader("📈 Parcours de la donnée")
        fig_funnel = go.Figure(go.Funnel(
            y=["Données DVF Brutes(20M)", "Sélection Résidentiel", "Filtres Métier / Outliers", "Dataset Consolidé"],
            x=[20100000, 12500000, 5200000, 4480000],
            textinfo="value+percent previous",
            marker=dict(color=[ "#1f4068", "#2a5a8a", "#17b978", "#00eaaf"])
        ))
        fig_funnel.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_funnel, use_container_width=True)

    st.markdown("---")

    # Répartition et Portrait-robot unifiés dans un seul bloc expander
    st.subheader("📊 Portrait-robot du marché résidentiel")
    with st.expander("🔍 Voir la répartition et les caractéristiques des biens (Surfaces, Pièces, Prix)", expanded=True):
        
        # On utilise 4 colonnes pour intégrer le camembert + les 3 histogrammes
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("<br>", unsafe_allow_html=True) # Petit alignement vertical
            fig_type = px.pie(values=[60, 40], names=["Appartements", "Maisons"], 
                              title="Type de biens",
                              color_discrete_sequence=['#1f4068', '#00eaaf'])
            fig_type.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_type, use_container_width=True)
            
        with col2:
            st.plotly_chart(px.histogram(df_raw_viz, x="surface_reelle_bati", title="Surfaces (m²)", 
                                         color_discrete_sequence=['#1f4068']), use_container_width=True)
        with col3:
            st.plotly_chart(px.histogram(df_raw_viz, x="nombre_pieces_principales", title="Pièces", 
                                         color_discrete_sequence=['#00eaaf']), use_container_width=True)
        with col4:
            st.plotly_chart(px.histogram(df_raw_viz, x="valeur_fonciere", title="Prix Vente (€)", 
                                         color_discrete_sequence=['#ff9f43']), use_container_width=True)


    st.success("🎤 **Ce travail de filtrage sélectif est le préalable indispensable à tout projet MLOps sérieux.")
# 
# ==================================================
# CONTENU ONGLET 2 : ENRICHISSEMENT
# ==================================================
with tab2:
    st.header("🧩 2. Enrichir la donnée : La puissance du multi-sources")
    st.markdown("##### *Objectif : Transformer une ligne de prix en un objet immobilier contextuel.*")

    if "show_sources" not in st.session_state:
        st.session_state.show_sources = False

    # Layout : Colonne de gauche (Pipeline) + Colonne de droite (Détail)
    col_main, col_detail = st.columns([1, 1.5])

    with col_main:
        st.subheader("🔗 Architecture du Pipeline")
        
        # Schéma Pipeline visuel (en texte stylisé/markdown)
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1f4068;">
            <p style="font-weight: bold; margin-bottom: 10px;">Entrées Multi-Sources :</p>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>✅ DVF (Etalab)</li>
                <li>✅ DPE (ADEME)</li>
                <li>✅ INSEE (Filosofi)</li>
                <li>✅ BPE (Services)</li>
                <li>✅ SNCF (Transports)</li>
                <li>✅ SSMSI (Sécurité)</li>
            </ul>
            <div style="text-align: center; font-size: 20px; font-weight: bold; color: #1f4068;">↓</div>
            <div style="background: #17b978; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">
                Dataset Enrichi (ML-Ready)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") 
        b_col1, b_col2 = st.columns([0.1, 0.9])
        with b_col2:
            if st.button("🔍 Voir le détail des sources", use_container_width=True):
                st.session_state.show_sources = not st.session_state.show_sources

    with col_detail:
        if st.session_state.show_sources:
            st.subheader("📋 Catalogue des sources")
            sources_df = pd.DataFrame({
                "Source": ["DVF", "DPE", "INSEE", "BPE", "SNCF", "SSMSI"],
                "Rôle": [
                    "Socle transactionnel (Prix m²).",
                    "Performance énergétique.",
                    "Attractivité communale.",
                    "Densité des équipements.",
                    "Proximité transport.",
                    "Taux de délinquance."
                ]
            })
            st.dataframe(sources_df, use_container_width=True, hide_index=True)
        else:
            # Ici on affiche le schéma du pipeline quand le détail est masqué
            st.subheader("📈 Flux de données")
            st.info("Le pipeline agrège 6 sources publiques pour enrichir le socle transactionnel DVF. Cliquez sur le bouton à gauche pour consulter les caractéristiques techniques de chaque source.")
            
    st.markdown("---")

    # --- FOCUS 1 : DPE ---
    st.markdown("#### ⚡ Focus 1 : L'appariement DPE (ADEME)")
    col_dpe_left, col_dpe_right = st.columns([1, 2])
    
    with col_dpe_left:
        data_fusion = {"Statut": ["DPE Apparié", "Indisponible"], "Volume": [1.35, 3.13]}
        fig_pie = px.pie(pd.DataFrame(data_fusion), values="Volume", names="Statut", 
                         hole=0.5, color_discrete_sequence=['#17b978', '#2c3e50'])
        fig_pie.update_layout(height=200, margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_dpe_right:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("**Pivot de jointure composite :** `Code Commune` + `Nom de Voie` + `Numéro`.")
        st.write("L'enrichissement DPE permet de calculer la corrélation entre **classe énergétique** et **décote immobilière**, une variable clé pour notre modèle prédictif.")

    st.markdown("---")

    # --- FOCUS 2 : CONTEXTE TERRITORIAL ---
    st.markdown("#### 👥 Focus 2 : Macro-contexte territorial & Local")
    tab_demo, tab_vie, tab_bpe, tab_secu = st.tabs(["👥 Démographie", "💰 Niveau de vie", "🏪 Services (BPE)", "🚔 Sécurité"])
    
    with tab_demo:
        c_left, c_right = st.columns(2)
        with c_left:
            st.code("Features : population_2023, evolution_pop_5_ans", language="text")
            st.markdown("Mesure la dynamique d'attractivité des communes, corrélée à la tension du marché.")
        with c_right:
            demo_sim = pd.DataFrame({"Dynamique": ["Déclin", "Stable", "Croissance"], "Prix": [1400, 2600, 4200]})
            st.plotly_chart(px.bar(demo_sim, x="Dynamique", y="Prix", color_discrete_sequence=['#00eaaf'], height=160), use_container_width=True)

    with tab_vie:
        c_left, c_right = st.columns(2)
        with c_left:
            st.code("Features : revenu_median, taux_pauvrete", language="text")
            st.markdown("Modélise le pouvoir d'achat intrinsèque des ménages résidents.")
        with c_right:
            st.plotly_chart(px.scatter(pd.DataFrame({"R": np.random.normal(22000, 4000, 100), "P": np.random.normal(2600, 500, 100)}), x="R", y="P", color_discrete_sequence=['#1f4068'], height=160), use_container_width=True)

    with tab_bpe:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("Normalisation des équipements communaux :")
            st.latex(r"\text{Indicateur} = \frac{\text{Nb Équipements}}{\text{Population}} \times 1000")
        with c_right:
            st.plotly_chart(px.bar(pd.DataFrame({"S": ["Commerces", "Écoles", "Santé"], "D": [12.4, 3.2, 4.5]}), x="D", y="S", orientation='h', color_discrete_sequence=['#ff9f43'], height=160), use_container_width=True)

    with tab_secu:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("**Réduction de la colinéarité :** Fusion de 17 variables ministérielles en 3 indicateurs synthétiques :")
            st.success("✓ `taux_violences` | ✓ `taux_vols` | ✓ `taux_stupefiants`")
        with c_right:
            st.plotly_chart(px.pie(pd.DataFrame({"T": ["Conservées", "Supprimées"], "N": [3, 14]}), values="N", names="T", hole=0.4, color_discrete_sequence=['#17b978', '#e0e0e0'], height=160), use_container_width=True)

    st.markdown("---")

    # --- FOCUS 3 : ACCESSIBILITÉ ---
    st.markdown("#### 🚉 Focus 3 : Accessibilité aux infrastructures (SNCF)")
    col_map, col_tree = st.columns([1.2, 0.8])
    
    with col_map:
        if FOLIUM_AVAILABLE:
            m = folium.Map(location=[45.76, 4.83], zoom_start=13)
            folium.Marker([45.755, 4.830], icon=folium.Icon(color="red", icon="home")).add_to(m)
            folium.Marker([45.764, 4.835], icon=folium.Icon(color="blue", icon="train")).add_to(m)
            st_folium(m, width=500, height=220)
        else:
            st.info("📍 Vecteur de calcul spatial : [Mutation DVF] ➔ Linear Distance ➔ [Gare SNCF]")

    with col_tree:
        st.markdown("**Le défi technique : performance spatiale**")
        st.markdown("Associer des millions de coordonnées via des arbres K-D.")
        st.code("from scipy.spatial import cKDTree\ntree = cKDTree(gares_coords)\ndist, _ = tree.query(biens_coords)", language="python")
        st.success("⚡ Performance : Calcul France entière < 0.4s.")



with tab3:
    st.header("⚙️ 3. Feature Engineering & Robustesse")
    
    # 1. Comparaison visuelle immédiate (L'impact métier)
    col_avant, col_apres = st.columns(2)
    with col_avant:
        st.markdown("""<div style="border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; background: rgba(255,255,255,0.01);">
            <h6 style="color: #ff9f43;">❌ Avant le Feature Engineering</h6>
            <p style="font-size: 0.85rem; opacity: 0.8;">Modèle aveugle au contexte : il ne perçoit le bien que par ses dimensions brutes (m², pièces).</p>
        </div>""", unsafe_allow_html=True)
    with col_apres:
        st.markdown("""<div style="border: 1px solid #17b978; padding: 15px; border-radius: 8px; background: rgba(23,185,120,0.03);">
            <h6 style="color: #17b978;">✔ Après le Feature Engineering</h6>
            <p style="font-size: 0.85rem;">Compréhension holistique : le modèle croise géométrie, pouvoir d'achat, accès transports et performance énergétique.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Audit et Imputation (Le sérieux technique)
    col_na, col_audit = st.columns([1, 1])
    with col_na:
        st.markdown("**🛡️ Stratégie d'imputation (Missing Values)**")
        na_df = pd.DataFrame({
            "Nature": ["Pop/Revenus", "Sécurité", "DPE absent"],
            "Méthode": ["Médiane locale", "Valeur 0 (Constatée)", "Drapeau binaire (`has_dpe=0`)"]
        })
        st.table(na_df) # st.table est plus propre ici que st.dataframe pour une petite liste
        
    with col_audit:
        st.markdown("**⚙️ Automatisation QC (Contrôle Qualité)**")
        st.markdown("""
        1. **`isnull()`** : Audit strict du taux de complétion.
        2. **`describe()`** : Éradication des anomalies statistiques.
        3. **`corr()`** : Filtrage des features colinéaires (réduction de dimension).
        """)

    # 3. L'inventaire des variables
    with st.expander("📂 Les variables métiers générées", expanded=True):
        v1, v2, v3 = st.columns(3)
        v1.markdown("**🏠 Logement**\n<small>`is_maison`, `surface_par_piece`, `age_construction`</small>", unsafe_allow_html=True)
        v2.markdown("**📍 Territoire**\n<small>`dist_gare_km`, `is_metropole`, `taux_pauvrete`</small>", unsafe_allow_html=True)
        v3.markdown("**⚡ Énergie**\n<small>`dpe_num`, `cout_usage`, `has_dpe`</small>", unsafe_allow_html=True)

    # 4. Transition MLOps
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1f4068 0%, #162447 100%); padding: 22px; border-radius: 10px; border-left: 6px solid #00eaaf;">
        <h4 style="color:#00eaaf !important; margin-top:0; font-weight:700;">🔄 Du Script à l'Industrialisation MLOps</h4>
        <p style="font-size:0.95rem; color:#ffffff;">
            Pour garantir la <b>reproductibilité</b> de ces calculs et assurer une <b>gouvernance stricte</b>, nous avons industrialisé ce pipeline. 
            Découvrons maintenant comment nous assurons le tracking de ces variables avec <b>MLflow et DVC</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================================================
# CONTENU ONGLET 4 : MODÉLISATION (MACHINE LEARNING)
# ==================================================
with tab4:
    st.header("🤖 4. Modélisation : L'intelligence prédictive")
    st.markdown("##### *Objectif : Unifier la complexité du marché français au sein d'un modèle XGBoost unique et robuste.*")

    # 1. Le Protocole Expérimental
    st.subheader("1️⃣ Protocole Expérimental & Données")
    st.markdown("""
    Pour capturer la non-linéarité du marché, nous avons structuré un pipeline de modélisation unifié :
    - **Dataset :** 4,48 M de transactions (34 variables métier).
    - **Split :** 80% Entraînement (3,58 M) / 20% Test (895 k).
    - **Approche :** XGBoost unifié (Gradient Boosting) remplaçant les segmentations rigides par un apprentissage global.
    """)

    # 2. Le choix du Résiduel (La "Valeur Intrinsèque")
    col_res1, col_res2 = st.columns([1, 1.2])
    with col_res1:
        st.markdown("**🎯 Pourquoi prédire un résiduel ?**")
        st.latex(r"\text{Cible } (Y) = \text{Prix Réel} / m^2 - P_{\text{commune\_lissé}}")
        st.info("Le modèle ne prédit pas le prix global, mais la **surcote/décote locale**. Cela décharge l'algorithme de l'apprentissage de la carte brute des prix.")
    
    with col_res2:
        st.markdown("**⚙️ Lissage Bayésien**")
        st.latex(r"P_{\text{lissé}} = \frac{N_{\text{commune}} \cdot P_{\text{commune}} + K \cdot P_{\text{département}}}{N_{\text{commune}} + K}")
        st.caption("Assure une robustesse statistique même pour les petites communes avec peu de transactions.")

    st.markdown("---")

    # 3. Benchmark et Performance
    st.subheader("📊 Performance du modèle unifié")
    col_bench, col_metrics = st.columns([2, 1])
    
    with col_bench:
        models_perf = pd.DataFrame({
            'Modèle': ['Régression Linéaire', 'Ridge', 'ExtraTrees', 'LightGBM', 'Random Forest', 'XGBoost (Unifié)'],
            'MAPE (%)': [52.6, 52.6, 35.4, 34.7, 34.4, 31.45]
        }).sort_values(by='MAPE (%)', ascending=True)
        
        fig = px.bar(models_perf, x='MAPE (%)', y='Modèle', orientation='h', color='MAPE (%)', 
                     color_continuous_scale='Mint', title="Benchmark : Erreur moyenne par modèle (MAPE)")
        st.plotly_chart(fig, use_container_width=True)

    with col_metrics:
        st.metric(label="Précision Finale (R²)", value="0.80")
        st.metric(label="Erreur Moyenne (MAPE)", value="31.45 %")
        st.success("Le modèle unifié surpasse les segmentations manuelles grâce à sa capacité à croiser les dynamiques globales et locales.")

    # 4. Interprétabilité (Ce que le modèle voit)
    st.subheader("🧠 Analyse d'importance des features (SHAP)")
    col_feat, col_learn = st.columns(2)
    
    with col_feat:
        st.markdown("Top 5 variables déterminantes :")
        st.bar_chart(data=pd.DataFrame({'Importance': [32.4, 18.2, 11.5, 9.8, 8.1]}, 
                                       index=['Prix Commune', 'Surface Bâti', 'Latitude', 'Longitude', 'Revenu Médian']))

    with col_learn:
        st.markdown("Stabilité du modèle :")
        st.line_chart(data=np.array([178000, 120000, 95000, 85000, 80700]))
        st.caption("Convergence rapide vers l'erreur minimale (RMSE).")

    # 5. Synthèse & Transition Punchy
    st.markdown("---")
    st.success("""
    ### 💡 Synthèse de la modélisation
    - **Unicité :** Un seul modèle XGBoost apprend l'intégralité du marché.
    - **Robustesse :** Le lissage bayésien élimine le bruit des données locales.
    - **Performance :** R² de 0.80 sur l'ensemble de la France.
    - **Intrinsèque :** Le modèle capture la vraie valeur, indépendamment de la géographie brute.
    """)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #1f4068 0%, #162447 100%); padding: 20px; border-radius: 10px;">
        <h4 style="color:#00eaaf;">🚀 Industrialisation MLOps</h4>
        <p style="color:white;">Nous avons industrialisé ce pipeline pour garantir la reproductibilité. 
        Passons maintenant à la <b>Phase IV : Déploiement et Tracking</b> avec MLflow pour le suivi de nos expériences.</p>
    </div>
    """, unsafe_allow_html=True)