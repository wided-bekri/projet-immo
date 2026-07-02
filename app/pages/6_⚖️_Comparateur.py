"""
Page 3 - Comparateur de communes
Compagnon Immobilier
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Comparateur - Compagnon Immobilier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE, "data", "streamlit")
ASSET_DIR = os.path.join(BASE, "assets")

with open(os.path.join(ASSET_DIR, "style.css"), encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

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

communes = load_communes()

COULEURS = ["#1B3A4B", "#2E86AB", "#E07A5F", "#3D405B"]



st.markdown(
    """
    <h1 style="margin-bottom:0">Comparateur de communes</h1>
    <p style="color:#64748B;margin-top:0.3rem;font-size:1rem">
        Comparez jusqu'à 4 communes selon les principaux indicateurs
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ─── Sélection communes ───────────────────────────────────────────────────────
default = []
if st.session_state.get("commune_label", "") in communes["label"].tolist():
    default = [st.session_state["commune_label"]]

selection = st.multiselect(
    "Sélectionnez des communes (2 à 4)",
    options=communes["label"].tolist(),
    default=default,
    max_selections=4,
    placeholder="Tapez pour rechercher...",
)

if len(selection) < 2:
    st.info("Sélectionnez au moins 2 communes pour comparer.")
    st.stop()

# ─── Données des communes sélectionnées ──────────────────────────────────────
rows = communes[communes["label"].isin(selection)].set_index("label")

def fmt_prix(v):
    return f"{v:,.0f} €" if not pd.isna(v) else "N/A"

def fmt_pct(v):
    return f"{v:+.1f}%" if not pd.isna(v) else "N/A"

def fmt_int(v):
    return f"{int(v):,}".replace(",", " ") if not pd.isna(v) else "N/A"

# ─── Layout tableau + radar ───────────────────────────────────────────────────
col_table, col_radar = st.columns([5, 4], gap="large")

with col_table:
    st.subheader("Comparaison des indicateurs")

    indicateurs = [
        ("Prix médian (€/m²)",      "commune_prix_m2",      fmt_prix),
        ("Évolution 5 ans",          "evolution_5ans_pct",   fmt_pct),
        ("Revenu médian (€/an)",     "revenu_median",        fmt_prix),
        ("Population",               "population_2023",      fmt_int),
        ("Équipements (total)",      "nb_equipements_total", fmt_int),
        ("Score attractivité (/100)","score_attractivite",   lambda v: f"{v:.0f}/100" if not pd.isna(v) else "N/A"),
    ]

    # En-tête
    header_cols = st.columns([3] + [2] * len(selection))
    header_cols[0].markdown("**Indicateurs**")
    for i, label in enumerate(selection):
        nom = label.split(" (")[0]
        header_cols[i + 1].markdown(
            f"<span style='color:{COULEURS[i]};font-weight:700'>{nom}</span>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='margin:0.4rem 0'>", unsafe_allow_html=True)

    for lbl, col, fmt_fn in indicateurs:
        row_cols = st.columns([3] + [2] * len(selection))
        row_cols[0].markdown(f"<span style='color:#64748B;font-size:0.9rem'>{lbl}</span>", unsafe_allow_html=True)
        for i, label in enumerate(selection):
            val = rows.loc[label, col] if col in rows.columns and label in rows.index else np.nan
            row_cols[i + 1].markdown(
                f"<span style='color:{COULEURS[i]};font-weight:600'>{fmt_fn(val)}</span>",
                unsafe_allow_html=True,
            )
        st.markdown("<hr style='margin:0.3rem 0;opacity:0.3'>", unsafe_allow_html=True)

    # Score attractivité mis en évidence
    st.markdown("<br>", unsafe_allow_html=True)
    score_cols = st.columns(len(selection))
    for i, label in enumerate(selection):
        nom  = label.split(" (")[0]
        sc   = rows.loc[label, "score_attractivite"] if "score_attractivite" in rows.columns else np.nan
        score_cols[i].markdown(
            f"""
            <div style="background:{COULEURS[i]}18;border:2px solid {COULEURS[i]};
                        border-radius:10px;padding:0.8rem;text-align:center">
                <p style="margin:0;font-size:0.75rem;color:#64748B">{nom}</p>
                <p style="margin:0;font-size:1.6rem;font-weight:800;color:{COULEURS[i]}">
                    {sc:.0f}<span style="font-size:0.9rem">/100</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_radar:
    st.subheader("Profil comparatif")

    axes_radar = [
        ("score_immobilier",  "Immobilier"),
        ("score_dynamisme",   "Dynamisme"),
        ("score_revenus",     "Revenus"),
        ("score_equipements", "Equipements"),
        ("score_securite",    "Securite"),
        ("score_transport",   "Transport"),
    ]

    fig_radar = go.Figure()
    categories = [a[1] for a in axes_radar]

    for i, label in enumerate(selection):
        nom    = label.split(" (")[0]
        vals   = []
        for col, _ in axes_radar:
            v = rows.loc[label, col] if col in rows.columns and label in rows.index else 50
            vals.append(float(v) if not pd.isna(v) else 50)
        vals_closed = vals + [vals[0]]
        cats_closed = categories + [categories[0]]

        fig_radar.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=cats_closed,
            fill="toself",
            name=nom,
            line_color=COULEURS[i],
            opacity=0.6,
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.divider()

# ─── Info bas de page ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:#F1F5F9;border-radius:8px;padding:0.8rem 1rem;font-size:0.85rem;color:#64748B">
        💡 Le score d'attractivité combine 6 dimensions : Immobilier, Dynamisme, Revenus, Équipements, Sécurité, Transport.
        Source : DVF 2020-2024, INSEE, Filosofi, BPE, données de sécurité.
    </div>
    """,
    unsafe_allow_html=True,
)



