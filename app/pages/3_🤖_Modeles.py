import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
# Page
# ==================================================
# ==================================================
# BANDEAU D'INTRODUCTION
# ==================================================
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); padding: 40px; border-radius: 12px; margin-bottom: 30px; color: white; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 2.3rem;">🤖 PHASE III — Modélisation du marché immobilier français</h1>
        <p style="font-size: 1.15rem; opacity: 0.9; margin-top: 15px; max-width: 950px; margin-left: auto; margin-right: auto; line-height: 1.6;">
            Après avoir préparé plus de 4,4 millions de transactions enrichies, nous avons comparé plusieurs familles d'algorithmes afin d'identifier celle capable de capturer la complexité du marché immobilier français.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==================================================
# 1️⃣ LE PROTOCOLE EXPÉRIMENTAL
# ==================================================
st.header("1️⃣ Le protocole expérimental")

st.markdown(
    """
    <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(128,128,128,0.2); border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 25px;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
            <div style="background: #2c5364; padding: 15px; border-radius: 8px; min-width: 200px;">
                <span style="font-size: 1.2rem;">💎 Dataset Final</span><br><b>4,48 M transactions</b><br><span style="font-size: 0.8rem; opacity: 0.7;">34 variables</span>
            </div>
            <div style="font-size: 1.5rem;">➔</div>
            <div style="background: rgba(23, 185, 120, 0.1); border: 1px solid #17b978; padding: 12px; border-radius: 8px; min-width: 150px;">
                <span style="color: #17b978; font-weight: bold;">Train 80%</span><br><b>3,58 M</b>
            </div>
            <div style="background: rgba(255, 75, 75, 0.1); border: 1px solid #FF4B4B; padding: 12px; border-radius: 8px; min-width: 150px;">
                <span style="color: #FF4B4B; font-weight: bold;">Test 20%</span><br><b>895 k</b>
            </div>
            <div style="font-size: 1.5rem;">➔</div>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; min-width: 180px;">
                ⚙️ Benchmark modèles
            </div>
            <div style="font-size: 1.5rem;">➔</div>
            <div style="background: #17b978; color: white; padding: 15px; border-radius: 8px; min-width: 180px; font-weight: bold;">
                🏆 Architecture Finale
            </div>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

st.markdown("---")

# ==================================================
# 2️⃣ LA CONFRONTATION ALGORITHMIQUE
# ==================================================
st.header("2️⃣ La confrontation algorithmique")

col_bench, col_bench_win = st.columns([2, 1])

with col_bench:
    # Bar chart horizontal pour le Benchmark
    models_perf = pd.DataFrame({
        'Modèle': ['Régression Linéaire', 'Ridge', 'ExtraTrees', 'LightGBM', 'Random Forest', 'XGBoost Optimisé'],
        'MAPE (%)': [52.6, 52.6, 35.4, 34.7, 34.4, 34.1]
    }).sort_values(by='MAPE (%)', ascending=False)
    
    fig_bench = px.bar(
        models_perf, x='MAPE (%)', y='Modèle', orientation='h',
        title="Comparaison des modèles (Métrique : MAPE - Plus bas est meilleur)",
        text=[f"{x}%" for x in models_perf['MAPE (%)']],
        color='MAPE (%)', color_continuous_scale='Blues_r'
    )
    fig_bench.update_traces(textposition='outside')
    fig_bench.update_layout(showlegend=False, height=350, margin=dict(t=40, b=10, l=10, r=40))
    st.plotly_chart(fig_bench, use_container_width=True)

with col_bench_win:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 🏆 Algorithme retenu : XGBoost")
        st.metric(label="Précision (R²)", value="0.75")
        st.metric(label="Erreur Moyenne (MAPE)", value="34.1 %")
        st.caption("Le modèle de Gradient Boosting offre le meilleur compromis entre temps d'apprentissage et capture des non-linéarités du marché.")

st.markdown("---")

# ==================================================
# 3️⃣ POURQUOI PRÉDIR UN RÉSIDUEL ?
# ==================================================
st.header("3️⃣ Pourquoi prédire un résiduel ?")

col_res_vis, col_res_msg = st.columns([1, 1])

with col_res_vis:
    st.markdown(
        """
        <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(128,128,128,0.15); border-radius: 8px; padding: 20px; text-align: center;">
            <div style="display: flex; justify-content: space-around; align-items: center;">
                <div><span style="font-size: 0.9rem; opacity:0.8;">Prix Réel</span><br><b style="font-size: 1.4rem; color: #ffeb3b;">3 200 €/m²</b></div>
                <div style="font-size: 1.5rem;">−</div>
                <div><span style="font-size: 0.9rem; opacity:0.8;">Médian Communal</span><br><b style="font-size: 1.4rem;">2 800 €/m²</b></div>
                <div style="font-size: 1.5rem;">➔</div>
                <div style="background: rgba(23,185,120,0.2); padding: 10px; border-radius: 6px;">
                    <span style="font-size: 0.9rem; color: #17b978; font-weight:bold;">Résiduel</span><br><b style="font-size: 1.4rem; color: #17b978;">+400 €/m²</b>
                </div>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_res_msg:
    with st.container(border=True):
        st.markdown("#### 🎯 Message clé")
        st.markdown(
            """
            Le modèle n'apprend pas à reconstruire la macro-économie globale du marché français. 
            Il apprend uniquement à **évaluer une surcote ou une décote locale** basée sur les caractéristiques intrinsèques propres au logement.
            """
        )

st.markdown("---")

# ==================================================
# 4️⃣ UNE ARCHITECTURE SPÉCIALISÉE
# ==================================================
st.header("4️⃣ Une architecture spécialisée")

col_arch_tree, col_arch_table = st.columns([1, 1])

with col_arch_tree:
    st.markdown("#### 分 Segmentation multi-modèles")
    st.markdown(
        """
        <div style="background-color: rgba(255,255,255,0.02); border: 1px dashed rgba(128,128,128,0.3); border-radius: 8px; padding: 20px; font-family: monospace; line-height: 1.6;">
            🔹 <b>Bas de gamme</b><br>
            &nbsp;&nbsp;├─ 🏠 Maison (Modèle 1)<br>
            &nbsp;&nbsp;└─ 🏢 Appartement (Modèle 2)<br><br>
            🔸 <b>Milieu de gamme</b><br>
            &nbsp;&nbsp;├─ 🏠 Maison (Modèle 3)<br>
            &nbsp;&nbsp;└─ 🏢 Appartement (Modèle 4)<br><br>
            👑 <b>Haut de gamme</b><br>
            &nbsp;&nbsp;├─ 🏠 Maison (Modèle 5)<br>
            &nbsp;&nbsp;└─ 🏢 Appartement (Modèle 6)
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.info("💡 **6 modèles XGBoost indépendants** entraînés sur leurs sous-marchés respectifs.")

with col_arch_table:
    st.markdown("#### 📊 Seuils des segments de marché")
    segments_df = pd.DataFrame({
        "Segment": ["Bas", "Moyen", "Haut"],
        "Prix médian communal": ["< 1 800 €/m²", "1 800 – 3 100 €/m²", "> 3 100 €/m²"]
    })
    st.table(segments_df)

st.markdown("---")

# ==================================================
# 5️⃣ LES RÉSULTATS FINAUX (PERFORMANCES ACCRUES)
# ==================================================
st.header("5️⃣ Les résultats finaux")

col_perf_kpi, col_perf_gain = st.columns([3, 2])

with col_perf_kpi:
    with st.container(border=True):
        st.markdown("#### ✨ Métriques de performance de l'architecture")
        pkpi1, pkpi2, pkpi3, pkpi4 = st.columns(4)
        pkpi1.metric(label="📈 R² Final", value="0.81")
        pkpi2.metric(label="📉 MAE", value="617 €/m²")
        pkpi3.metric(label="📉 RMSE", value="983 €/m²")
        pkpi4.metric(label="🎯 MAPE Final", value="29.68 %")

with col_perf_gain:
    # Visualisation de l'amélioration de la MAPE
    fig_gain = go.Figure(go.Indicator(
        mode = "delta",
        value = 29.68,
        delta = {'reference': 30.4, 'relative': False, 'increasing': {'color': "#FF4B4B"}, 'decreasing': {'color': "#17b978"}},
        title = {"text": "Optimisation de la MAPE (Gain global)"}
    ))
    fig_gain.update_layout(height=160, margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig_gain, use_container_width=True)
    st.markdown("<p style='text-align: center; font-weight: bold; color: #17b978;'>📈 +0.72 point de précision gagné grâce à la segmentation</p>", unsafe_allow_html=True)

st.markdown("---")

# ==================================================
# 6️⃣ POURQUOI LE MODÈLE PREND-IL CETTE DÉCISION ?
# ==================================================
st.header("6️⃣ Pourquoi le modèle prend-il cette décision ?")

# Feature Importance Top 10
feat_imp_df = pd.DataFrame({
    'Feature': [
        'commune_prix_m2', 'surface_reelle_bati', 'latitude', 'longitude', 
        'revenu_median', 'transports_pour_1000', 'target_dpe_num', 
        'age_construction', 'population_2023', 'surface_par_piece'
    ],
    'Importance (%)': [32.4, 18.2, 11.5, 9.8, 8.1, 6.4, 5.2, 4.1, 2.3, 2.0]
}).sort_values(by='Importance (%)', ascending=True)

fig_feat = px.bar(
    feat_imp_df, x='Importance (%)', y='Feature', orientation='h',
    title="Top 10 Global Feature Importance (Valeurs de Shapley / Poids des nœuds)",
    color='Importance (%)', color_continuous_scale='Viridis'
)
fig_feat.update_layout(height=400, margin=dict(t=40, b=20, l=10, r=10))
st.plotly_chart(fig_feat, use_container_width=True)

st.markdown("---")

# ==================================================
# CONCLUSION DE LA PAGE
# ==================================================
st.subheader("💡 Résumé de l'étape de modélisation")
with st.container(border=True):
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("* **✓ 6 modèles spécialisés :** Division des tâches pour réduire la variance globale.")
        st.markdown("* **✓ Segmentation du marché :** Capacité à appréhender différemment le haut de gamme et le logement social.")
        st.markdown("* **✓ Prédiction des résiduels :** Simplification de la surface de perte de l'algorithme.")
    with cc2:
        st.markdown("* **✓ Protection Data Leakage :** Aucune donnée de validation n'a contaminé le dictionnaire de prix.")
        st.markdown("* **✓ Coefficient $R^2 = 0.81$ :** 81% de la variance du prix au m² est expliquée.")
        st.markdown("* **✓ MAPE finale de 29.68% :** Niveau de précision robuste pour une application à échelle nationale.")
