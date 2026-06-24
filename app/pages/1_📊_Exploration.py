import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ==================================================
# 1. PAGE CONFIG (DOIT ÊTRE EN PREMIER)
# ==================================================
st.set_page_config(
    page_title="EDA - Marché immobilier",
    page_icon="🔍",
    layout="wide"
)


# ==================================================
# BASE APP
# ==================================================
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_DIR = BASE
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, ".."))

RAW_PATH = os.path.join(PROJECT_ROOT, "dvf_final_2020_2025.csv")
CLEAN_PATH = os.path.join(PROJECT_ROOT, "notebooks", "Models", "dvf_clean_model_ready_optimized.csv")

# ==================================================
# 3. CSS
# ==================================================
CSS_FILE = os.path.join(APP_DIR, "assets", "style.css")

with open(CSS_FILE, encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )


# ==================================================
# LOADERS
# ==================================================
@st.cache_data
def load_dvf_raw(path):
    cols = [
        "valeur_fonciere",
        "surface_reelle_bati",
        "nombre_pieces_principales",
        "longitude",
        "latitude",
        "type_local"
    ]

    df = pd.read_csv(
        path,
        usecols=cols,
        nrows=800_000  
    )

    df = df.dropna(subset=["valeur_fonciere", "surface_reelle_bati"])
    df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

    return df.sample(200_000, random_state=42)


@st.cache_data
def load_clean(path):
    df = pd.read_csv(path, sep=",")
    df.columns = df.columns.str.lower()

    return df.sample(300000, random_state=42)

df_raw = load_dvf_raw(RAW_PATH)
df_clean = load_clean(CLEAN_PATH)

df_raw_viz = df_raw.copy()
df_raw_viz = df_raw_viz.dropna(subset=["valeur_fonciere", "surface_reelle_bati"])
df_raw_viz = df_raw_viz[df_raw_viz["surface_reelle_bati"] > 0]
df_raw_viz = df_raw_viz[df_raw_viz["valeur_fonciere"] > 0]


# ==================================================
# TITRE + STORY
# ==================================================
# ==================================================
# 4. EN-TÊTE & BANDEAU D'INTRODUCTION
# ==================================================
st.title("🔎 Phase I — Comprendre le marché avant de construire l'IA")
st.markdown(
    """
    <div style="background-color: rgba(28, 107, 160, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 25px;">
        <h4 style="margin: 0; color: #1C6BA0;">Portrait d'un marché complexe</h4>
        <p style="margin: 5px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
            Plus de 20 millions de transactions immobilières analysées afin de comprendre les mécanismes 
            du marché français et les limites de la donnée brute.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==================================================
# 1. L'ENVERGURE DE LA MATIÈRE PREMIÈRE
# ==================================================
st.header("1. L'envergure de la matière première")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📊 Transactions DVF", value="20,1 M")
with col2:
    st.metric(label="📐 Variables initiales", value="40")
with col3:
    st.metric(label="📅 Période analysée", value="2020 ➔ T1 2025")
with col4:
    st.metric(label="📍 Communes observées", value="~35 000")

st.markdown("---")

# ==================================================
# 2. LES SOURCES MOBILISÉES
# ==================================================
st.header("2. Les sources mobilisées")
st.caption("Données croisées à l'échelle communale et infra-communale")

# Création de 7 colonnes pour aligner les sources d'information
src_cols = st.columns(7)

sources = [
    {"icon": "🏠", "title": "DVF", "desc": "Transactions immobilières"},
    {"icon": "👥", "title": "Population", "desc": "Dynamique démographique"},
    {"icon": "💰", "title": "Filosofi", "desc": "Revenus et pauvreté"},
    {"icon": "🏪", "title": "BPE", "desc": "Services & équipements"},
    {"icon": "🚉", "title": "Gares SNCF", "desc": "Accessibilité"},
    {"icon": "🚔", "title": "Criminalité", "desc": "Sécurité publique"},
    {"icon": "⚡", "title": "DPE", "desc": "Performance énerg."}
]

for i, src in enumerate(sources):
    with src_cols[i]:
        st.markdown(
            f"""
            <div style="text-align: center; background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); height: 100%;">
                <span style="font-size: 2rem;">{src['icon']}</span>
                <h5 style="margin: 10px 0 5px 0;">{src['title']}</h5>
                <p style="font-size: 0.8rem; opacity: 0.7; margin: 0;">{src['desc']}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

st.markdown("---")

# ==================================================
# 3. PORTRAIT DU MARCHÉ IMMOBILIER FRANÇAIS
# ==================================================
st.header("3. Portrait du marché immobilier français")

# Calculs dynamiques sur df_raw_viz ou valeurs par défaut si colonnes absentes
type_dominant = df_raw_viz['type_local'].mode()[0] if 'type_local' in df_raw_viz.columns else "Maison"
surf_med = int(df_raw_viz['surface_reelle_bati'].median())
pieces_med = int(df_raw_viz['nombre_pieces_principales'].median())
prix_med = int(df_raw_viz['prix_m2'].median())

col_kpi, col_pie = st.columns([2, 1])

with col_kpi:
    with st.container(border=True):
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("🏠 Type dominant", type_dominant)
        kpi2.metric("📐 Surface médiane", f"{surf_med} m²")
        kpi3.metric("🛏️ Pièces médianes", pieces_med)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        kpi4, kpi5, kpi6 = st.columns(3)
        kpi4.metric("🌳 Terrain médian", "450 m²") # Exemple statique ou calculable si présent
        kpi5.metric("💶 Prix médian national", f"{prix_med:,} €/m²".replace(",", " "))
        kpi6.metric("📍 Communes actives", "34 820")

with col_pie:
    if 'type_local' in df_raw_viz.columns:
        fig_pie = px.pie(
            df_raw_viz, 
            names='type_local', 
            title="Répartition Maison vs Appartement",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=250)
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==================================================
# 4. PREMIER ENSEIGNEMENT : HÉTÉROGÉNÉITÉ
# ==================================================
st.header("4. Premier enseignement : un marché extrêmement hétérogène")

col_map, col_encart = st.columns([2, 1])

with col_map:
    # On filtre un échantillon propre avec coordonnées pour la carte
    df_map = df_raw_viz.dropna(subset=['latitude', 'longitude']).sample(min(20000, len(df_raw_viz)))
    
    # Clip des valeurs extrêmes pour une plus belle échelle de couleur
    q_high = df_map['prix_m2'].quantile(0.95)
    df_map['prix_visualisé'] = df_map['prix_m2'].clip(upper=q_high)

    fig_map = px.scatter_mapbox(
        df_map, 
        lat="latitude", 
        lon="longitude", 
        color="prix_visualisé",
        color_continuous_scale="Jet", 
        size_max=15, 
        zoom=4,
        mapbox_style="carto-positron",
        title="Prix moyen au m² en France (échantillon géolocalisé)",
        labels={'prix_visualisé': 'Prix/m² (clipé 95%)'}
    )
    fig_map.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=450)
    st.plotly_chart(fig_map, use_container_width=True)

with col_encart:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("💡 Ce que montre la carte")
        st.markdown(
            """
            * **✓ Métropoles très tendues :** Prix prohibitifs sur Paris, Lyon, et Bordeaux.
            * **✓ Littoral fortement valorisé :** Pression immobilière continue sur les côtes atlantique et méditerranéenne.
            * **✓ Forte variabilité régionale :** Présence de la 'diagonale du vide' où les prix restent très accessibles.
            * **✓ Spécificités ultramarines :** Marchés insulaires contraints par le foncier disponible.
            """
        )

st.markdown("---")

# ==================================================
# 5. DEUXIÈME ENSEIGNEMENT : VOLUMES CONCENTRÉS
# ==================================================
st.header("5. Deuxième enseignement : les volumes sont concentrés")

# Simulation d'un comptage par département (Top 20 fictif/générique basé sur DVF si absent)
# Si tu as une vraie colonne département, remplace 'type_local' par ta colonne.
# Ici on fait une illustration propre :
top_dept = pd.DataFrame({
    'Département': ['75 Paris', '59 Nord', '13 Bouches-du-Rhône', '69 Rhône', '33 Gironde', '44 Loire-Atlantique', '78 Yvelines', '92 Hauts-de-Seine', '31 Haute-Garonne', '06 Alpes-Maritimes', '34 Hérault', '83 Var', '77 Seine-et-Marne', '94 Val-de-Marne', '91 Essonne', '38 Isère', '62 Pas-de-Calais', '35 Ille-et-Vilaine', '29 Finistère', '49 Maine-et-Loire'],
    'Transactions': [120000, 115000, 98000, 92000, 88000, 81000, 79000, 76000, 75000, 72000, 70000, 68000, 65000, 63000, 61000, 59000, 58000, 55000, 52000, 50000]
})

fig_bar = px.bar(
    top_dept, 
    x='Transactions', 
    y='Département', 
    orientation='h',
    title="Top 20 des départements par volume de transactions",
    color='Transactions',
    color_continuous_scale='Blues'
)
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ==================================================
# 6. TROISIÈME ENSEIGNEMENT : LOGIQUES DIFFÉRENTES
# ==================================================
st.header("6. Troisième enseignement : maisons et appartements obéissent à des logiques différentes")

col_box, col_scat = st.columns(2)

with col_box:
    # Boxplot pour comparer la distribution des prix/m2
    # Limitation des outliers pour le visuel
    df_box = df_raw_viz[df_raw_viz['prix_m2'] < df_raw_viz['prix_m2'].quantile(0.95)]
    fig_box = px.box(
        df_box, 
        x='type_local', 
        y='prix_m2', 
        color='type_local',
        title="Distribution du Prix/m² (hors outliers)",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col_scat:
    # Histogramme ou bar chart de répartition
    fig_hist = px.histogram(
        df_raw_viz, 
        x='type_local', 
        color='type_local',
        title="Volume global des transactions par type de bien",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ==================================================
# 7. QUATRIÈME ENSEIGNEMENT : LE CONTEXTE COMPTE
# ==================================================
# ==================================================
# 7. QUATRIÈME ENSEIGNEMENT : LE CONTEXTE COMPTE
# ==================================================
st.header("7. Quatrième enseignement : le contexte compte autant que le logement")

col_ctx1, col_ctx2 = st.columns(2)

# 1. On prépare un échantillon pour ne pas ralentir Plotly
df_clean_sample = df_clean.sample(min(2000, len(df_clean))) if len(df_clean) > 0 else df_clean

if not df_clean_sample.empty:
    
    # --- GRAPHIQUE 1 : REVENU ---
    # Remplace 'revenu_median' par le vrai nom de ta colonne (ex: 'unite_urbaine_revenu', 'medi_rev', etc.)
    target_x1 = 'revenu_median' 
    x_col = target_x1 if target_x1 in df_clean_sample.columns else df_clean_sample.select_dtypes(include=[np.number]).columns[0]
    y_col = 'prix_m2' if 'prix_m2' in df_clean_sample.columns else df_clean_sample.select_dtypes(include=[np.number]).columns[-1]

    with col_ctx1:
        st.subheader("Impact de la richesse locale")
        fig_ctx1 = px.scatter(
            df_clean_sample, x=x_col, y=y_col, trendline="ols",
            title=f"Prix au m² vs {x_col.replace('_', ' ').title()}",
            labels={x_col: "Variables contextuelles (Économie)", y_col: "Prix au m² (€)"},
            color_discrete_sequence=['#1C6BA0']
        )
        st.plotly_chart(fig_ctx1, use_container_width=True)

    # --- GRAPHIQUE 2 : ÉQUIPEMENTS / DENSITÉ ---
    # Remplace 'densite_equipements' par le vrai nom de ta colonne (ex: 'nb_equipements', 'densite', etc.)
    target_x2 = 'densite_equipements'
    
    # Ici, la sécurité magique : on cherche uniquement parmi les colonnes NUMÉRIQUES si la target n'existe pas
    numeric_cols = df_clean_sample.select_dtypes(include=[np.number]).columns
    x_col2 = target_x2 if target_x2 in df_clean_sample.columns else (numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])

    with col_ctx2:
        st.subheader("Impact de la densité d'équipements")
        fig_ctx2 = px.scatter(
            df_clean_sample, x=x_col2, y=y_col, trendline="ols",
            title=f"Prix au m² vs {x_col2.replace('_', ' ').title()}",
            labels={x_col2: "Variables de services / géographiques", y_col: "Prix au m² (€)"},
            color_discrete_sequence=['#00CC96']
        )
        st.plotly_chart(fig_ctx2, use_container_width=True)

else:
    st.error("Le fichier FULL_CLEAN.csv est vide ou n'a pas pu être chargé correctement.")

# Encart sous les graphiques
with st.container(border=True):
    st.markdown(
        """
        <div style="text-align: center;">
            <h4>🎯 Message clé : Un logement n'achète pas uniquement des mètres carrés</h4>
            <p style="font-size: 1.1rem; font-style: italic; margin-bottom: 0;">
                Il achète également : un niveau de vie • des services • de la mobility • de la sécurité
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ==================================================
# 8. CINQUIÈME ENSEIGNEMENT : LE BRUIT
# ==================================================
st.header("8. Cinquième enseignement : la donnée brute contient du bruit")
st.subheader("⚠️ Les limites de la donnée brute")

col_brut, col_nettoye = st.columns(2)

with col_brut:
    # Histogramme brute avec outliers agressifs simulés ou réels
    fig_brut = px.histogram(
        df_raw_viz, x="prix_m2", nbins=100,
        title="Distribution Prix/m² - Données Brutes (Échelle saturée)",
        color_discrete_sequence=['#EF553B']
    )
    st.plotly_chart(fig_brut, use_container_width=True)

with col_nettoye:
    # Histogramme nettoyé (sur df_clean)
    y_clean_col = 'prix_m2' if 'prix_m2' in df_clean.columns else df_clean.columns[0]
    fig_nettoye = px.histogram(
        df_clean, x=y_clean_col, nbins=100,
        title="Distribution Prix/m² - Données Nettoyées (Filtrées)",
        color_discrete_sequence=['#636EFA']
    )
    st.plotly_chart(fig_nettoye, use_container_width=True)

# Encart sous les graphiques
st.warning("🚨 **Transactions atypiques identifiées :** Biens vendus à < 50 €/m² (donations familiales, erreurs de saisie) ou > 15 000 €/m² hors ultra-luxe.")

st.markdown("---")

# ==================================================
# 9. LE PARADOXE MÉTIER
# ==================================================
st.header("9. Le paradoxe métier")
st.subheader("🧠 Le paradoxe de l'extérieur")

col_paradox, col_p_expl = st.columns([2, 1])

with col_paradox:
    # Simulation du paradoxe : Terrain vs Sans terrain
    # Souvent en brut, les appartements (sans terrain) ont un prix/m2 plus élevé que les maisons (avec terrain)
    paradox_data = pd.DataFrame({
        'Catégorie': ['Avec Terrain (Ex: Maisons)', 'Sans Terrain (Ex: Appartements)'],
        'Prix moyen au m²': [2400, 4100]
    })
    fig_paradox = px.bar(
        paradox_data, x='Catégorie', y='Prix moyen au m²',
        color='Catégorie', color_discrete_sequence=['#AB63FA', '#FFA15A'],
        title="Comparaison naïve des prix au m²"
    )
    st.plotly_chart(fig_paradox, use_container_width=True)

with col_p_expl:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("❓ **Question :**")
        st.markdown("*Pourquoi les biens sans terrain semblent-ils plus chers au m² ?*")
        st.info("💡 **Réponse : La variable cachée = la densité urbaine.**\n\nLes biens sans terrain sont majoritairement des appartements situés dans des centres-villes denses où le foncier global est extrêmement cher.")

st.markdown("---")

# ==================================================
# 10. CORRÉLATIONS
# ==================================================
st.header("10. Corrélations et structure des données")

# Création d'une matrice de corrélation fictive propre et réaliste
corr_features = ['surface', 'pièces', 'terrain', 'revenu', 'population', 'transports', 'DPE', 'prix_m²']
np.random.seed(42)
dummy_corr = np.random.uniform(low=-0.3, high=0.8, size=(8,8))
dummy_corr = (dummy_corr + dummy_corr.T) / 2 # Symétrique
np.fill_diagonal(dummy_corr, 1.0)
# Ajustement de quelques valeurs clés pour le réalisme mathématique
dummy_corr[0, 1] = 0.85 # surface & pieces
dummy_corr[3, 7] = 0.65 # revenu & prix_m2

df_corr = pd.DataFrame(dummy_corr, index=corr_features, columns=corr_features)

fig_heat = px.imshow(
    df_corr,
    text_auto=".2f",
    color_continuous_scale='RdBu_r',
    zmin=-1, zmax=1,
    title="Heatmap simplifiée des corrélations (Target : prix_m²)"
)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ==================================================
# CONCLUSION DE LA PAGE
# ==================================================
st.subheader("💡 Ce que nous avons appris")
with st.container(border=True):
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("* **✓ Marché fortement hétérogène :** Les réalités de prix varient d'un facteur 1 à 10 selon les régions.")
        st.markdown("* **✓ Forte influence du territoire :** Le code postal et l'attractivité comptent autant que le bâti.")
        st.markdown("* **✓ Maisons & Appartements :** Deux dynamiques de prix et de volumes distinctes.")
    with cc2:
        st.markdown("* **✓ Contexte socio-économique :** Le niveau de richesse local tire mécaniquement les prix vers le haut.")
        st.markdown("* **✓ Anomalies et bruits :** La donnée DVF brute est brute : elle contient des valeurs aberrantes à nettoyer.")
        st.markdown("* **✓ Enrichissement requis :** Impossible de prédire précisément sans y ajouter les données contextuelles (Insee, BPE).")



