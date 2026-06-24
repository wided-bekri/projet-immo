"""
Page 2 - Evolution des prix
Compagnon Immobilier
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Evolution - Compagnon Immobilier",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE, "data", "streamlit")
ASSET_DIR = os.path.join(BASE, "assets")

with open(os.path.join(ASSET_DIR, "style.css"), encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

@st.cache_data(show_spinner="Chargement des donnees...")
def load_evolution():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "evolution_prix_communes.csv"),
        dtype={"code_commune": str, "code_departement": str},
        encoding="utf-8",
    )
    df["code_commune"]     = df["code_commune"].str.zfill(5)
    df["code_departement"] = df["code_departement"].str.zfill(2)
    return df

@st.cache_data(show_spinner="Chargement des communes...")
def load_communes():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "communes_streamlit.csv"),
        dtype={"code_commune": str, "code_departement": str},
        encoding="utf-8",
    )
    df["code_commune"]     = df["code_commune"].str.zfill(5)
    df["code_departement"] = df["code_departement"].str.zfill(2)
    df["label"] = df["nom_commune"] + " (" + df["code_departement"] + ")"
    return df.sort_values("label").reset_index(drop=True)

df_evo     = load_evolution()
communes   = load_communes()



# ─── En-tete ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom:0">Evolution des prix</h1>
    <p style="color:#64748B;margin-top:0.3rem;font-size:1rem">
        Historique 2020-2024 — Donnees DVF
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ─── Filtres ─────────────────────────────────────────────────────────────────
# Pré-remplir depuis session_state si vient de page Estimation
default_commune = st.session_state.get("commune_label", "")

col_f1, col_f2 = st.columns([3, 2])
with col_f1:
    commune_label = st.selectbox(
        "Commune",
        options=[""] + communes["label"].tolist(),
        index=([""] + communes["label"].tolist()).index(default_commune)
        if default_commune in communes["label"].tolist() else 0,
    )
with col_f2:
    type_bien = st.selectbox(
        "Type de bien",
        options=["Tous", "Maison", "Appartement"],
    )

if not commune_label:
    st.info("Selectionnez une commune pour afficher l'evolution des prix.")
    st.stop()

# ─── Données filtrées ─────────────────────────────────────────────────────────
code_commune = communes[communes["label"] == commune_label]["code_commune"].values[0]
nom_commune  = communes[communes["label"] == commune_label]["nom_commune"].values[0]

df_commune = df_evo[df_evo["code_commune"] == code_commune].sort_values("annee")

if df_commune.empty:
    st.warning(f"Pas de données disponibles pour {nom_commune}.")
    st.stop()

# Colonnes selon type
if type_bien == "Maison":
    col_prix = "prix_m2_median_maison"
    col_vol  = "nb_transactions_maison"
elif type_bien == "Appartement":
    col_prix = "prix_m2_median_appart"
    col_vol  = "nb_transactions_appart"
else:
    col_prix = "prix_m2_median_tous"
    col_vol  = "nb_transactions_tous"

df_plot = df_commune[["annee", col_prix, col_vol]].dropna(subset=[col_prix])

if df_plot.empty:
    st.warning(f"Pas de données de type '{type_bien}' pour {nom_commune}.")
    st.stop()

# ─── KPIs ─────────────────────────────────────────────────────────────────────
prix_actuel  = df_plot[col_prix].iloc[-1]
prix_depart  = df_plot[col_prix].iloc[0]
evol_5ans    = (prix_actuel - prix_depart) / prix_depart * 100 if prix_depart > 0 else 0
annee_actuel = int(df_plot["annee"].iloc[-1])
vol_actuel   = int(df_plot[col_vol].iloc[-1]) if not pd.isna(df_plot[col_vol].iloc[-1]) else 0

col_main, col_kpi = st.columns([7, 3], gap="large")

with col_kpi:
    st.markdown(
        f"""
        <div style="background:#F8FAFC;border-radius:12px;padding:1.2rem;margin-bottom:1rem;border:1px solid #E2E8F0">
            <p style="color:#64748B;font-size:0.8rem;margin:0">Prix actuel</p>
            <p style="font-size:1.8rem;font-weight:800;color:#1B3A4B;margin:0.2rem 0">
                {prix_actuel:,.0f} €/m²</p>
            <p style="color:#94A3B8;font-size:0.8rem;margin:0">Annee {annee_actuel}</p>
        </div>
        <div style="background:#F8FAFC;border-radius:12px;padding:1.2rem;margin-bottom:1rem;border:1px solid #E2E8F0">
            <p style="color:#64748B;font-size:0.8rem;margin:0">Evolution sur la periode</p>
            <p style="font-size:1.8rem;font-weight:800;color:{'#16A34A' if evol_5ans >= 0 else '#DC2626'};margin:0.2rem 0">
                {evol_5ans:+.1f}%</p>
            <p style="color:#94A3B8;font-size:0.8rem;margin:0">{int(df_plot['annee'].iloc[0])} - {annee_actuel}</p>
        </div>
        <div style="background:#F8FAFC;border-radius:12px;padding:1.2rem;border:1px solid #E2E8F0">
            <p style="color:#64748B;font-size:0.8rem;margin:0">Transactions ({annee_actuel})</p>
            <p style="font-size:1.8rem;font-weight:800;color:#1B3A4B;margin:0.2rem 0">
                {vol_actuel:,}</p>
            <p style="color:#94A3B8;font-size:0.8rem;margin:0">Nombre de ventes</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_main:
    # ── Graphique ligne prix ──────────────────────────────────────────────
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_plot["annee"],
        y=df_plot[col_prix],
        mode="lines+markers",
        name="Prix median au m²",
        line=dict(color="#1B3A4B", width=3),
        marker=dict(size=8, color="#1B3A4B"),
        fill="tozeroy",
        fillcolor="rgba(27,58,75,0.06)",
    ))
    fig_line.update_layout(
        title="Prix median au m²",
        xaxis_title="",
        yaxis_title="€/m²",
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(tickmode="linear", dtick=1),
        yaxis=dict(tickformat=",.0f"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ── Graphique barres volume ───────────────────────────────────────────
    df_vol = df_plot.dropna(subset=[col_vol])
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_vol["annee"],
        y=df_vol[col_vol],
        name="Transactions",
        marker_color="#1B3A4B",
        opacity=0.8,
    ))
    fig_bar.update_layout(
        title="Volume de transactions",
        xaxis_title="",
        yaxis_title="Nombre de transactions",
        height=250,
        margin=dict(l=10, r=10, t=40, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(tickmode="linear", dtick=1),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ─── Tableau recap ────────────────────────────────────────────────────────────
st.divider()
st.subheader("Tableau récapitulatif")
df_table = df_plot.copy()
df_table[col_prix] = df_table[col_prix].apply(lambda x: f"{x:,.0f} €/m²")
df_table[col_vol]  = df_table[col_vol].apply(lambda x: f"{int(x):,}" if not pd.isna(x) else "N/A")
df_table["annee"]  = df_table["annee"].astype(int)
df_table.columns   = ["Année", "Prix médian au m²", "Transactions"]
st.dataframe(df_table.set_index("Année"), use_container_width=True)

st.markdown(
    "<p style='color:#94A3B8;font-size:0.8rem;margin-top:1rem'>"
    "Source : Demandes de Valeurs Foncières (DVF) — data.gouv.fr</p>",
    unsafe_allow_html=True,
)



