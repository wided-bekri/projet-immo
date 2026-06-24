"""
Page 4 - Carte nationale des prix
Compagnon Immobilier
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os

st.set_page_config(
    page_title="Carte - Compagnon Immobilier",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE, "data", "streamlit")
ASSET_DIR = os.path.join(BASE, "assets")

with open(os.path.join(ASSET_DIR, "style.css"), encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

@st.cache_data(show_spinner="Chargement de la carte...")
def load_carte():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "carte_prix_departements.csv"),
        dtype={"code_departement": str},
        encoding="utf-8",
    )
    df["code_departement"] = df["code_departement"].str.zfill(2)
    return df

@st.cache_data(show_spinner="Chargement du GeoJSON...")
def load_geojson():
    with open(os.path.join(DATA_DIR, "departements.geojson"), encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner="Chargement des communes...")
def load_communes():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "communes_streamlit.csv"),
        dtype={"code_commune": str, "code_departement": str},
        encoding="utf-8",
    )
    df["code_departement"] = df["code_departement"].str.zfill(2)
    return df

df_carte  = load_carte()
geojson   = load_geojson()
communes  = load_communes()



st.markdown(
    """
    <h1 style="margin-bottom:0">Carte des prix</h1>
    <p style="color:#64748B;margin-top:0.3rem;font-size:1rem">
        Prix médian au m² par département — Données DVF
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ─── Filtres ──────────────────────────────────────────────────────────────────
annees_dispo = sorted(df_carte["annee"].unique())
col_f1, col_f2 = st.columns(2)
with col_f1:
    annee_sel = st.selectbox("Année", options=annees_dispo, index=len(annees_dispo) - 1)
with col_f2:
    type_sel = st.selectbox("Type de bien", options=["Tous", "Maison", "Appartement"])

# Colonne selon type
if type_sel == "Maison":
    col_prix = "prix_m2_median_maison"
    label_prix = "Prix médian Maison (€/m²)"
elif type_sel == "Appartement":
    col_prix = "prix_m2_median_appart"
    label_prix = "Prix médian Appartement (€/m²)"
else:
    col_prix = "prix_m2_median_tous"
    label_prix = "Prix médian tous biens (€/m²)"

df_filtre = df_carte[df_carte["annee"] == annee_sel].copy()
df_filtre = df_filtre.dropna(subset=[col_prix])

# Stats département depuis communes
dept_stats = communes.groupby("code_departement").agg(
    revenu_median=("revenu_median", "median"),
    score_attractivite=("score_attractivite", "median"),
    evolution_5ans_pct=("evolution_5ans_pct", "median"),
).reset_index()
df_filtre = df_filtre.merge(dept_stats, on="code_departement", how="left")

# ─── Layout carte + detail ────────────────────────────────────────────────────
col_map, col_detail = st.columns([7, 3], gap="large")

with col_map:
    fig = px.choropleth(
        df_filtre,
        geojson=geojson,
        locations="code_departement",
        featureidkey="properties.code",
        color=col_prix,
        color_continuous_scale=[
            [0.0,  "#FFFDE7"],
            [0.15, "#FFF9C4"],
            [0.3,  "#C8E6C9"],
            [0.45, "#80CBC4"],
            [0.65, "#26A69A"],
            [0.8,  "#00695C"],
            [1.0,  "#1B3A4B"],
        ],
        range_color=[df_filtre[col_prix].quantile(0.05), df_filtre[col_prix].quantile(0.95)],
        labels={col_prix: "€/m²"},
        hover_name="code_departement",
        hover_data={col_prix: ":,.0f", "nb_transactions": ":,"},
    )
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        showcoastlines=False,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        coloraxis_colorbar=dict(
            title="€/m²",
            tickformat=",.0f",
            len=0.6,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "<p style='color:#94A3B8;font-size:0.78rem'>Données agrégées par département. "
        "Les valeurs représentent les médianes des transactions DVF.</p>",
        unsafe_allow_html=True,
    )

with col_detail:
    st.markdown("#### Détail par département")

    dept_liste = sorted(df_filtre["code_departement"].tolist())
    DEPT_NOMS = {
        "01":"Ain","02":"Aisne","03":"Allier","04":"Alpes-de-Haute-Provence",
        "05":"Hautes-Alpes","06":"Alpes-Maritimes","07":"Ardèche","08":"Ardennes",
        "09":"Ariège","10":"Aube","11":"Aude","12":"Aveyron","13":"Bouches-du-Rhône",
        "14":"Calvados","15":"Cantal","16":"Charente","17":"Charente-Maritime",
        "18":"Cher","19":"Corrèze","2A":"Corse-du-Sud","2B":"Haute-Corse",
        "21":"Côte-d'Or","22":"Côtes-d'Armor","23":"Creuse","24":"Dordogne",
        "25":"Doubs","26":"Drôme","27":"Eure","28":"Eure-et-Loir","29":"Finistère",
        "30":"Gard","31":"Haute-Garonne","32":"Gers","33":"Gironde","34":"Hérault",
        "35":"Ille-et-Vilaine","36":"Indre","37":"Indre-et-Loire","38":"Isère",
        "39":"Jura","40":"Landes","41":"Loir-et-Cher","42":"Loire","43":"Haute-Loire",
        "44":"Loire-Atlantique","45":"Loiret","46":"Lot","47":"Lot-et-Garonne",
        "48":"Lozère","49":"Maine-et-Loire","50":"Manche","51":"Marne",
        "52":"Haute-Marne","53":"Mayenne","54":"Meurthe-et-Moselle","55":"Meuse",
        "56":"Morbihan","57":"Moselle","58":"Nièvre","59":"Nord","60":"Oise",
        "61":"Orne","62":"Pas-de-Calais","63":"Puy-de-Dôme","64":"Pyrénées-Atlantiques",
        "65":"Hautes-Pyrénées","66":"Pyrénées-Orientales","67":"Bas-Rhin",
        "68":"Haut-Rhin","69":"Rhône","70":"Haute-Saône","71":"Saône-et-Loire",
        "72":"Sarthe","73":"Savoie","74":"Haute-Savoie","75":"Paris",
        "76":"Seine-Maritime","77":"Seine-et-Marne","78":"Yvelines","79":"Deux-Sèvres",
        "80":"Somme","81":"Tarn","82":"Tarn-et-Garonne","83":"Var","84":"Vaucluse",
        "85":"Vendée","86":"Vienne","87":"Haute-Vienne","88":"Vosges","89":"Yonne",
        "90":"Territoire de Belfort","91":"Essonne","92":"Hauts-de-Seine",
        "93":"Seine-Saint-Denis","94":"Val-de-Marne","95":"Val-d'Oise",
    }
    dept_sel = st.selectbox(
        "Département",
        options=dept_liste,
        format_func=lambda x: f"{x} — {DEPT_NOMS.get(x, x)}"
    )

    row = df_filtre[df_filtre["code_departement"] == dept_sel]

    if not row.empty:
        row = row.iloc[0]

        prix_val  = row.get(col_prix, np.nan)
        nb_trans  = row.get("nb_transactions", np.nan)
        revenu    = row.get("revenu_median", np.nan)
        score     = row.get("score_attractivite", np.nan)
        evol      = row.get("evolution_5ans_pct", np.nan)

        # Calcul évolution prix departement
        df_dept_hist = df_carte[
            (df_carte["code_departement"] == dept_sel)
        ].sort_values("annee")
        if len(df_dept_hist) >= 2:
            p_debut = df_dept_hist[col_prix].dropna().iloc[0]  if not df_dept_hist[col_prix].dropna().empty else np.nan
            p_fin   = df_dept_hist[col_prix].dropna().iloc[-1] if not df_dept_hist[col_prix].dropna().empty else np.nan
            evol_dept = (p_fin - p_debut) / p_debut * 100 if p_debut and p_debut > 0 else np.nan
        else:
            evol_dept = np.nan

        st.markdown(
            f"""
            <div style="background:#F8FAFC;border-radius:12px;padding:1.2rem;border:1px solid #E2E8F0">
                <p style="font-size:1.1rem;font-weight:700;color:#1B3A4B;margin:0">
                    📍 Département {dept_sel}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        indicateurs = [
            ("€", "Prix médian au m²",         f"{prix_val:,.0f} €/m²"  if not pd.isna(prix_val) else "N/A",  "#1B3A4B"),
            ("📈", "Évolution sur la période",  f"{evol_dept:+.1f}%"     if not pd.isna(evol_dept) else "N/A", "#16A34A" if not pd.isna(evol_dept) and evol_dept >= 0 else "#DC2626"),
            ("📋", "Transactions",              f"{int(nb_trans):,}".replace(",", " ") if not pd.isna(nb_trans) else "N/A", "#1B3A4B"),
            ("👤", "Revenu médian",             f"{revenu:,.0f} €".replace(",", " ")   if not pd.isna(revenu)   else "N/A", "#1B3A4B"),
            ("⭐", "Score attractivité",         f"{score:.0f} / 100"     if not pd.isna(score)   else "N/A",  "#F59E0B"),
        ]

        for icon, lbl, val, color in indicateurs:
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:0.6rem 0;border-bottom:1px solid #F1F5F9">
                    <span style="color:#64748B;font-size:0.88rem">{icon} {lbl}</span>
                    <span style="font-weight:700;color:{color};font-size:0.95rem">{val}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Évolution historique mini-chart
        st.markdown("<br>", unsafe_allow_html=True)
        if not df_dept_hist.empty and not df_dept_hist[col_prix].dropna().empty:
            import plotly.graph_objects as go
            fig_mini = go.Figure()
            df_mini  = df_dept_hist[["annee", col_prix]].dropna()
            fig_mini.add_trace(go.Scatter(
                x=df_mini["annee"], y=df_mini[col_prix],
                mode="lines+markers",
                line=dict(color="#1B3A4B", width=2),
                marker=dict(size=6),
            ))
            fig_mini.update_layout(
                height=180,
                margin=dict(l=0, r=0, t=10, b=0),
                plot_bgcolor="white",
                paper_bgcolor="white",
                xaxis=dict(tickmode="linear", dtick=1, tickfont=dict(size=10)),
                yaxis=dict(tickformat=",.0f", tickfont=dict(size=10)),
                showlegend=False,
            )
            st.plotly_chart(fig_mini, use_container_width=True)

        if st.button("Voir l'estimation pour ce département →", use_container_width=True):
            st.switch_page("pages/1_🏡_Estimation.py")




