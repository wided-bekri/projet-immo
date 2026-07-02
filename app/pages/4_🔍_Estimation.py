"""
Page 1 - Analyse d'un territoire & Estimation
Compagnon Immobilier
"""
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime

st.set_page_config(
    page_title="Estimation - Compagnon Immobilier",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(os.path.dirname(BASE), "notebooks", "Models")
DATA_DIR  = os.path.join(BASE, "data", "streamlit")
ASSET_DIR = os.path.join(BASE, "assets")
GARES_PATH = os.path.join(os.path.dirname(BASE), "liste-des-gares.csv")

with open(os.path.join(ASSET_DIR, "style.css"), encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)

# ─── Chargement données ───────────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des communes...")
def load_communes():
    df = pd.read_csv(
        os.path.join(DATA_DIR, "communes_streamlit.csv"),
        dtype={"code_commune": str, "code_departement": str},
    )
    df["code_commune"]     = df["code_commune"].str.zfill(5)
    df["code_departement"] = df["code_departement"].str.zfill(2)
    df["label"] = df["nom_commune"] + " (" + df["code_departement"] + ")"
    return df.sort_values("label").reset_index(drop=True)

@st.cache_resource(show_spinner="Chargement du modele...")
def load_models():
    meta = pickle.load(open(os.path.join(MODEL_DIR, "meta_6modeles.pkl"), "rb"))
    models = {}
    for tranche in ("bas", "milieu", "haut"):
        for t in ("maison", "appart"):
            path = os.path.join(MODEL_DIR, f"model_xgb_{tranche}_{t}.pkl")
            models[f"{tranche}_{t}"] = pickle.load(open(path, "rb"))
    return meta, models

@st.cache_data(show_spinner=False)
def load_gares():
    try:
        df = pd.read_csv(GARES_PATH, sep=";", encoding="utf-8",
                         usecols=["LIBELLE","VOYAGEURS","X_WGS84","Y_WGS84"])
        return df[df["VOYAGEURS"] == "O"].dropna(subset=["X_WGS84","Y_WGS84"])
    except:
        return pd.DataFrame()

communes    = load_communes()
meta, models = load_models()
FEATURES    = meta["features"]
Q33, Q66    = float(meta["q33"]), float(meta["q66"])
gares_df    = load_gares()

DPE_NUM = {"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"Non renseigne":4}

# ─── Utilitaires ──────────────────────────────────────────────────────────────
def dept_to_int(code):
    code = str(code).zfill(2).upper()
    if code == "2A": return 201.0
    if code == "2B": return 202.0
    try: return float(int(code))
    except: return 0.0

def get_tranche(pm2):
    if pm2 < Q33: return "bas"
    elif pm2 <= Q66: return "milieu"
    return "haut"

def fmt_eur(v):  return f"{v:,.0f} €".replace(",", " ")
def fmt_pm2(v):  return f"{v:,.0f} €/m²".replace(",", " ")
def fmt_pct(v, decimals=1):
    color = "#16A34A" if v >= 0 else "#DC2626"
    arrow = "📈" if v >= 0 else "📉"
    return f'<span style="color:{color};font-weight:700">{arrow} {v:+.{decimals}f}%</span>'

def haversine(lat1, lon1, lat2_arr, lon2_arr):
    R = 6371
    dlat = np.radians(lat2_arr - lat1)
    dlon = np.radians(lon2_arr - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2_arr)) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

def kpi_card(title, value, subtitle="", color="#1B3A4B", bg="#F8FAFC"):
    return f"""
    <div style="background:{bg};border-radius:10px;padding:1rem;border:1px solid #E2E8F0;height:100%">
        <p style="color:#64748B;font-size:0.8rem;margin:0">{title}</p>
        <p style="color:{color};font-size:1.6rem;font-weight:800;margin:0.2rem 0">{value}</p>
        <p style="color:#94A3B8;font-size:0.78rem;margin:0">{subtitle}</p>
    </div>"""

def section_header(icon, title, color="#1B3A4B"):
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:0.5rem;margin:1.5rem 0 0.8rem 0'>"
        f"<span style='font-size:1.3rem'>{icon}</span>"
        f"<span style='font-size:1.1rem;font-weight:700;color:{color}'>{title}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ─── Noms départements ────────────────────────────────────────────────────────
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

# ─── En-tête ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <h1 style="margin-bottom:0">Analyser un territoire</h1>
    <p style="color:#64748B;margin-top:0.3rem;font-size:1rem">
        Prix immobilier, démographie, transports, services, sécurité — tout en un coup d'œil
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ─── Formulaire ───────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns([2, 3, 2, 2])

with f1:
    dept_options = sorted(communes["code_departement"].unique())
    dept_sel = st.selectbox(
        "Département",
        options=[""] + dept_options,
        format_func=lambda x: "Tous" if x == "" else f"{x} — {DEPT_NOMS.get(x, '')}",
    )

with f2:
    communes_filtrees = communes[communes["code_departement"] == dept_sel] if dept_sel else communes
    commune_label = st.selectbox(
        "Commune",
        options=[""] + communes_filtrees["label"].tolist(),
        index=0,
    )

with f3:
    type_bien = st.selectbox("Type de bien", ["Appartement", "Maison"])
    is_maison_flag = 1 if type_bien == "Maison" else 0

with f4:
    surface_input = st.number_input(
        "Surface (m²) — optionnel",
        min_value=1, max_value=1000,
        value=None, step=1,
        placeholder="Ex: 70"
    )
    surface = float(surface_input) if surface_input else None

    nb_pieces_input = st.number_input(
        "Nombre de pièces — optionnel",
        min_value=0, max_value=20,
        value=None, step=1,
        placeholder="Ex: 3"
    )
    nb_pieces = float(nb_pieces_input) if nb_pieces_input is not None else 3.0

    dpe_classe = st.selectbox(
        "Classe DPE — optionnel",
        options=["Non renseigne", "A", "B", "C", "D", "E", "F", "G"],
        index=0,
        help="A = très économe, G = passoire thermique"
    )


# ─── Affichage automatique dès commune sélectionnée ──────────────────────────
if not commune_label:
    st.markdown(
        """
        <div style="display:flex;align-items:center;justify-content:center;
                    height:300px;color:#94A3B8;flex-direction:column;gap:1rem">
            <span style="font-size:3rem">🏡</span>
            <p style="font-size:1rem;margin:0">Sélectionnez un département et une commune</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

row = communes[communes["label"] == commune_label].iloc[0]
nom = row["nom_commune"]

# Détecter si c'est un arrondissement
is_arrondissement = any(x in nom for x in ["Arrondissement", "arrondissement"])

st.divider()

if is_arrondissement:
    st.info(
        f"ℹ️ **{nom}** est un arrondissement. Les données démographiques, économiques "
        f"et de services ne sont pas disponibles à ce niveau — elles sont rattachées "
        f"à la ville principale. Seuls les prix immobiliers et les transports sont affichés."
    )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — PRIX IMMOBILIER
# ══════════════════════════════════════════════════════════════════════════════
section_header("💶", "Prix immobilier")

col_type   = "commune_prix_m2_maison" if is_maison_flag else "commune_prix_m2_appart"
col_dept   = "dept_prix_m2_maison"    if is_maison_flag else "dept_prix_m2_appart"
pm2_type   = float(row.get(col_type, np.nan))
if pd.isna(pm2_type) or pm2_type <= 0:
    pm2_type = float(row.get(col_dept, np.nan))
if pd.isna(pm2_type) or pm2_type <= 0:
    pm2_type = float(row["commune_prix_m2"])

pm2_global    = float(row["commune_prix_m2"])
pm2_maison    = float(row.get("commune_prix_m2_maison", np.nan))
pm2_appart    = float(row.get("commune_prix_m2_appart", np.nan))
pm2_dept      = float(row.get("dept_prix_m2", np.nan))
evol_5ans     = float(row.get("evolution_5ans_pct", np.nan))
evol_1an      = float(row.get("evolution_1an_pct", np.nan))
volume        = int(row.get("commune_volume", 0) or 0)

p1, p2, p3, p4 = st.columns(4)
with p1:
    st.markdown(kpi_card(
        f"Prix médian {type_bien}",
        fmt_pm2(pm2_type),
        f"{nom}",
        color="#1B3A4B", bg="#F0F9FF"
    ), unsafe_allow_html=True)
with p2:
    if not is_maison_flag and not pd.isna(pm2_maison) and pm2_maison > 0:
        st.markdown(kpi_card("🏠 Prix médian Maison", fmt_pm2(pm2_maison), f"dans {nom}"), unsafe_allow_html=True)
    elif is_maison_flag and not pd.isna(pm2_appart) and pm2_appart > 0:
        st.markdown(kpi_card("🏢 Prix médian Appartement", fmt_pm2(pm2_appart), f"dans {nom}"), unsafe_allow_html=True)
with p3:
    st.markdown(kpi_card(
        "Prix médian département",
        fmt_pm2(pm2_dept) if not pd.isna(pm2_dept) else "N/A",
        f"Département {row['code_departement']}",
    ), unsafe_allow_html=True)
with p4:
    st.markdown(kpi_card(
        "Transactions enregistrées",
        f"{volume:,}".replace(",", " "),
        "DVF 2020-2025",
    ), unsafe_allow_html=True)

# Estimation si surface fournie
if surface:
    prix_est  = pm2_type * surface
    prix_bas  = prix_est * 0.85
    prix_haut = prix_est * 1.15
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1B3A4B,#2D5A73);
                    border-radius:12px;padding:1.5rem 2rem;color:white">
            <p style="margin:0;font-size:0.9rem;opacity:0.8">
                Estimation pour {int(surface)} m² — {type_bien} — {nom}
            </p>
            <p style="margin:0.3rem 0;font-size:2.5rem;font-weight:800">{fmt_eur(prix_est)}</p>
            <p style="margin:0;font-size:0.95rem;opacity:0.8">
                Fourchette indicative (±15%) : {fmt_eur(prix_bas)} — {fmt_eur(prix_haut)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not is_arrondissement:
    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — DÉMOGRAPHIE
    # ══════════════════════════════════════════════════════════════════════════
    section_header("👥", "Démographie")

    pop       = row.get("population_2023", np.nan)
    evol_pop5 = row.get("evolution_pop_5_ans", np.nan)
    evol_pop10= row.get("evolution_pop_10_ans", np.nan)

    if not pd.isna(evol_pop5) and abs(evol_pop5) < 1:
        evol_pop5 = evol_pop5 * 100
    if not pd.isna(evol_pop10) and abs(evol_pop10) < 1:
        evol_pop10 = evol_pop10 * 100

    d1, = st.columns(1)
    with d1:
        st.markdown(kpi_card(
            "Population (2023)",
            f"{int(float(pop)):,}".replace(",", " ") if not pd.isna(pop) else "N/A",
            "habitants"
        ), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — ÉCONOMIE
    # ══════════════════════════════════════════════════════════════════════════
    section_header("💰", "Économie")

    revenu   = row.get("revenu_median", np.nan)
    pauvrete = row.get("taux_pauvrete", np.nan)

    e1, e2 = st.columns(2)
    with e1:
        st.markdown(kpi_card(
            "Revenu médian",
            f"{int(float(revenu)):,} €/an".replace(",", " ") if not pd.isna(revenu) else "N/A",
            "Revenu fiscal médian par ménage",
            color="#16A34A" if not pd.isna(revenu) and revenu > 25000 else "#F59E0B"
        ), unsafe_allow_html=True)
    with e2:
        st.markdown(kpi_card(
            "Taux de pauvreté",
            f"{pauvrete:.1f}%" if not pd.isna(pauvrete) else "N/A",
            "Part de la population sous le seuil de pauvreté",
            color="#DC2626" if not pd.isna(pauvrete) and pauvrete > 15 else "#16A34A"
        ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — TRANSPORTS
# ══════════════════════════════════════════════════════════════════════════════
section_header("🚉", "Transports")

dist_gare = row.get("distance_gare_km", np.nan)
lat_c = float(row["latitude"])
lon_c = float(row["longitude"])

t1, t2 = st.columns([2, 3])

with t1:
    st.markdown(kpi_card(
        "Gare la plus proche",
        f"{dist_gare:.1f} km" if not pd.isna(dist_gare) else "N/A",
        "Distance à pied estimée",
        color="#16A34A" if not pd.isna(dist_gare) and dist_gare < 2
               else ("#F59E0B" if not pd.isna(dist_gare) and dist_gare < 10 else "#DC2626")
    ), unsafe_allow_html=True)

with t2:
    if not gares_df.empty:
        gares_copy = gares_df.copy()
        gares_copy["dist_km"] = haversine(lat_c, lon_c, gares_copy["Y_WGS84"].values, gares_copy["X_WGS84"].values)
        # Dédupliquer par nom de gare, garder la plus proche
        gares_copy = gares_copy.sort_values("dist_km").drop_duplicates(subset=["LIBELLE"])
        top5 = gares_copy.nsmallest(5, "dist_km")[["LIBELLE","dist_km"]]
        st.markdown("**🚉 Gares voyageurs les plus proches**")
        for _, g in top5.iterrows():
            d = g["dist_km"]
            color = "#16A34A" if d < 2 else ("#F59E0B" if d < 10 else "#DC2626")
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;padding:0.4rem 0;"
                f"border-bottom:1px solid #F1F5F9'>"
                f"<span style='font-size:0.9rem;color:#1B3A4B'>🚉 {g['LIBELLE']}</span>"
                f"<span style='font-weight:700;color:{color}'>{d:.1f} km</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

if is_arrondissement:
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SERVICES & ÉQUIPEMENTS
# ══════════════════════════════════════════════════════════════════════════════
section_header("🏪", "Services & Équipements")

def safe_int(val):
    try:
        v = row.get(val, np.nan)
        return int(v) if not pd.isna(v) else 0
    except:
        return 0

nb_total    = safe_int("nb_equipements_total")
nb_sante    = safe_int("nb_equipements_dom_D")
nb_ecoles   = safe_int("nb_equipements_dom_C")
nb_commerce = safe_int("nb_equipements_dom_B")

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(kpi_card("🏥 Santé", str(nb_sante), "médecins, hôpitaux, pharmacies", color="#7C3AED"), unsafe_allow_html=True)
with s2:
    st.markdown(kpi_card("🏫 Éducation", str(nb_ecoles), "écoles, collèges, lycées", color="#2563EB"), unsafe_allow_html=True)
with s3:
    st.markdown(kpi_card("🛒 Commerces", str(nb_commerce), "commerces de proximité", color="#D97706"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — SÉCURITÉ
# ══════════════════════════════════════════════════════════════════════════════
section_header("🔒", "Sécurité")

cambriolages = row.get("taux_cambriolages", np.nan)
vols         = row.get("taux_vols_total", np.nan)
violences    = row.get("taux_violences_total", np.nan)
score_secu   = row.get("score_securite", np.nan)

sec1, sec2, sec3, sec4 = st.columns(4)
with sec1:
    st.markdown(kpi_card(
        "Cambriolages",
        f"{cambriolages:.2f} ‰" if not pd.isna(cambriolages) else "N/A",
        "pour 1 000 habitants",
        color="#DC2626" if not pd.isna(cambriolages) and cambriolages > 5 else "#16A34A"
    ), unsafe_allow_html=True)
with sec2:
    st.markdown(kpi_card(
        "Vols",
        f"{vols:.2f} ‰" if not pd.isna(vols) else "N/A",
        "pour 1 000 habitants",
        color="#DC2626" if not pd.isna(vols) and vols > 10 else "#16A34A"
    ), unsafe_allow_html=True)
with sec3:
    st.markdown(kpi_card(
        "Violences",
        f"{violences:.2f} ‰" if not pd.isna(violences) else "N/A",
        "pour 1 000 habitants",
        color="#DC2626" if not pd.isna(violences) and violences > 8 else "#16A34A"
    ), unsafe_allow_html=True)
with sec4:
    st.markdown(kpi_card(
        "Score sécurité",
        f"{score_secu:.0f}/100" if not pd.isna(score_secu) else "N/A",
        "score calculé",
        color="#16A34A" if not pd.isna(score_secu) and score_secu >= 60 else "#F59E0B"
    ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SCORE ATTRACTIVITÉ GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
section_header("⭐", "Score d'attractivité global")

scores = {
    "Immobilier":   row.get("score_immobilier",  np.nan),
    "Dynamisme":    row.get("score_dynamisme",   np.nan),
    "Revenus":      row.get("score_revenus",     np.nan),
    "Équipements":  row.get("score_equipements", np.nan),
    "Sécurité":     row.get("score_securite",    np.nan),
    "Transport":    row.get("score_transport",   np.nan),
}
score_global = row.get("score_attractivite", np.nan)

sc_cols = st.columns(len(scores))
for i, (label, val) in enumerate(scores.items()):
    with sc_cols[i]:
        color = "#16A34A" if not pd.isna(val) and val >= 65 else ("#F59E0B" if not pd.isna(val) and val >= 40 else "#DC2626")
        st.markdown(kpi_card(
            label,
            f"{val:.0f}/100" if not pd.isna(val) else "N/A",
            "",
            color=color
        ), unsafe_allow_html=True)

if not pd.isna(score_global):
    color_g = "#16A34A" if score_global >= 65 else ("#F59E0B" if score_global >= 40 else "#DC2626")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:{color_g}18;border:2px solid {color_g};
                    border-radius:12px;padding:1rem 2rem;
                    display:flex;align-items:center;justify-content:space-between">
            <span style="font-size:1rem;font-weight:600;color:#1B3A4B">
                ⭐ Score d'attractivité global — {nom}
            </span>
            <span style="font-size:2rem;font-weight:800;color:{color_g}">
                {score_global:.0f} / 100
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — IMPACT DPE
# ══════════════════════════════════════════════════════════════════════════════
section_header("⚡", "Impact du DPE sur la valeur du bien")

# Impact par classe DPE (basé sur les données réelles 2025)
DPE_IMPACT = {
    "A":            (+23.0, "#16A34A", "Très bien isolé — forte valorisation"),
    "B":            (+14.0, "#22C55E", "Bien isolé — valorisation positive"),
    "C":            (+5.6,  "#86EFAC", "Correct — légère valorisation"),
    "Non renseigne":(0.0,   "#94A3B8", "Impact neutre — DPE non connu"),
    "D":            (-1.4,  "#F59E0B", "Classe moyenne — impact quasi neutre"),
    "E":            (-9.2,  "#F97316", "Énergivore — décote modérée"),
    "F":            (-16.6, "#EF4444", "Passoire thermique — forte décote"),
    "G":            (-20.0, "#DC2626", "Très mauvais — décote maximale + interdit à la location"),
}

impact_pct, impact_color, impact_label = DPE_IMPACT.get(dpe_classe, (0.0, "#94A3B8", ""))

dpe_col1, dpe_col2 = st.columns([1, 2])

with dpe_col1:
    # Badge DPE
    dpe_colors = {"A":"#16A34A","B":"#22C55E","C":"#86EFAC","D":"#F59E0B",
                  "E":"#F97316","F":"#EF4444","G":"#DC2626","Non renseigne":"#94A3B8"}
    bg = dpe_colors.get(dpe_classe, "#94A3B8")
    st.markdown(
        f"""
        <div style="background:{bg};border-radius:12px;padding:1.5rem;text-align:center">
            <p style="color:white;font-size:0.85rem;margin:0;font-weight:600">Classe DPE</p>
            <p style="color:white;font-size:3.5rem;font-weight:900;margin:0.2rem 0;line-height:1">{dpe_classe}</p>
            <p style="color:white;font-size:0.8rem;margin:0;opacity:0.9">{impact_label}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with dpe_col2:
    st.markdown(
        f"""
        <div style="background:#F8FAFC;border-radius:12px;padding:1.2rem;border:1px solid #E2E8F0">
            <p style="color:#64748B;font-size:0.85rem;margin:0">Impact sur le prix par rapport à un DPE médian (D)</p>
            <p style="font-size:2rem;font-weight:800;color:{impact_color};margin:0.3rem 0">
                {impact_pct:+.1f}%
            </p>
            <p style="color:#64748B;font-size:0.82rem;margin:0">
                Depuis la crise énergétique de 2022, l'impact du DPE sur les prix
                s'est fortement amplifié. Un logement classé G peut perdre jusqu'à
                <b>20%</b> de sa valeur par rapport à un logement équivalent classé A.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if dpe_classe in ("F", "G"):
        st.error("⚠️ Attention : les logements classés F et G sont interdits à la location depuis 2025. Cela impacte fortement leur valeur de revente.")
    elif dpe_classe in ("A", "B"):
        st.success("✅ Excellent DPE — votre bien bénéficie d'une valorisation positive sur le marché actuel.")

st.session_state["commune_label"] = commune_label
st.session_state["commune_code"]  = row["code_commune"]

st.markdown(
    """
    <p class="disclaimer">
    Estimations basées sur DVF 2020-2025 + DPE ADEME. Modèle XGBoost
    (R²=0.8101, MAPE=29.71%). Pour une valorisation précise, consultez un professionnel.
    </p>
    """,
    unsafe_allow_html=True,
)



