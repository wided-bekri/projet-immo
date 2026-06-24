"""
PREPARATION DES DONNEES STREAMLIT - Compagnon Immobilier
=========================================================
Genere 3 CSV legers pour l'application :
  - communes_streamlit.csv
  - evolution_prix_communes.csv
  - carte_prix_departements.csv

+ Telecharge le GeoJSON des departements francais.
Duree estimee : 5-10 minutes.
"""
import os, sys, requests, warnings
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree
warnings.filterwarnings("ignore")

BASE = r"C:\Users\a\Desktop\Projet Immo"
OUT  = os.path.join(BASE, "app", "data", "streamlit")
os.makedirs(OUT, exist_ok=True)

print("=" * 60)
print("  PREPARATION DES DONNEES STREAMLIT")
print("=" * 60)

# ── 1. CHARGEMENT DVF ─────────────────────────────────────────
print("\n[1/6] Chargement DVF (5.8M lignes)...")
DVF_COLS = ["annee", "prix_m2", "type_local", "code_departement",
            "code_commune", "nom_commune", "latitude", "longitude",
            "surface_reelle_bati", "nombre_pieces_principales"]
dvf = pd.read_csv(
    os.path.join(BASE, "dvf_final_2020_2025.csv"),
    usecols=DVF_COLS, low_memory=False,
    dtype={"code_commune": str, "code_departement": str}
)
dvf["code_commune"]     = dvf["code_commune"].str.zfill(5)
dvf["code_departement"] = dvf["code_departement"].str.zfill(2)
dvf = dvf[dvf["prix_m2"].between(300, 15_000)]
dvf["is_maison"] = (dvf["type_local"] == "Maison").astype(int)
print(f"   -> {len(dvf):,} transactions | {dvf['code_commune'].nunique():,} communes | {dvf['annee'].nunique()} annees")

# ── 2. ENRICHISSEMENTS ────────────────────────────────────────
print("\n[2/6] Chargement enrichissements INSEE + gares...")
comm_feats = pd.read_csv(
    os.path.join(BASE, "features_communes_clean.csv"),
    dtype={"code_commune": str}
)
comm_feats["code_commune"] = comm_feats["code_commune"].str.zfill(5)

gares_raw = pd.read_csv(os.path.join(BASE, "liste-des-gares.csv"), sep=";")
gares_voy = gares_raw[gares_raw["VOYAGEURS"] == "O"].dropna(
    subset=["X_WGS84", "Y_WGS84"]
).copy()
print(f"   -> {len(comm_feats):,} communes INSEE | {len(gares_voy):,} gares voyageurs")

# ── 3. STATS COMMUNALES ───────────────────────────────────────
print("\n[3/6] Calcul statistiques communales...")

centroids = (dvf.groupby("code_commune")
               .agg(nom_commune=("nom_commune", "first"),
                    code_departement=("code_departement", "first"),
                    latitude=("latitude", "median"),
                    longitude=("longitude", "median"))
               .reset_index())

def commune_stats(df, suffix=""):
    return (df.groupby("code_commune")
              .agg(**{f"commune_prix_m2{suffix}": ("prix_m2", "median"),
                      f"commune_volume{suffix}":   ("prix_m2", "count")})
              .reset_index())

stats_global = commune_stats(dvf, "")
stats_maison = commune_stats(dvf[dvf["is_maison"] == 1], "_maison")
stats_appart = commune_stats(dvf[dvf["is_maison"] == 0], "_appart")

dept_global = (dvf.groupby("code_departement")["prix_m2"]
                  .median().rename("dept_prix_m2").reset_index())
dept_maison = (dvf[dvf["is_maison"]==1].groupby("code_departement")["prix_m2"]
                  .median().rename("dept_prix_m2_maison").reset_index())
dept_appart = (dvf[dvf["is_maison"]==0].groupby("code_departement")["prix_m2"]
                  .median().rename("dept_prix_m2_appart").reset_index())

communes = (centroids
    .merge(stats_global, on="code_commune", how="left")
    .merge(stats_maison, on="code_commune", how="left")
    .merge(stats_appart, on="code_commune", how="left")
    .merge(dept_global,  on="code_departement", how="left")
    .merge(dept_maison,  on="code_departement", how="left")
    .merge(dept_appart,  on="code_departement", how="left")
)

# Lissage bayesien k=15 (meme que le modele)
def bayesian_smooth(commune_prix, commune_vol, dept_prix, k=15):
    n   = commune_vol.fillna(0)
    raw = commune_prix.fillna(dept_prix)
    return (n * raw + k * dept_prix) / (n + k)

communes["commune_prix_m2"]        = bayesian_smooth(communes["commune_prix_m2"],        communes["commune_volume"],        communes["dept_prix_m2"])
communes["commune_prix_m2_maison"] = bayesian_smooth(communes["commune_prix_m2_maison"], communes["commune_volume_maison"], communes["dept_prix_m2_maison"])
communes["commune_prix_m2_appart"] = bayesian_smooth(communes["commune_prix_m2_appart"], communes["commune_volume_appart"], communes["dept_prix_m2_appart"])

# Evolution 5 ans (2020 -> 2024)
prix_2020 = (dvf[dvf["annee"]==2020].groupby("code_commune")["prix_m2"]
               .median().rename("commune_prix_m2_2020").reset_index())
prix_2024 = (dvf[dvf["annee"]==2024].groupby("code_commune")["prix_m2"]
               .median().rename("commune_prix_m2_2024").reset_index())
communes = communes.merge(prix_2020, on="code_commune", how="left")
communes = communes.merge(prix_2024, on="code_commune", how="left")
communes["evolution_5ans_pct"] = (
    (communes["commune_prix_m2_2024"] - communes["commune_prix_m2_2020"])
    / communes["commune_prix_m2_2020"] * 100
).round(1)

# Evolution 1 an (2023 -> 2024)
prix_2023 = (dvf[dvf["annee"]==2023].groupby("code_commune")["prix_m2"]
               .median().rename("commune_prix_m2_2023").reset_index())
communes = communes.merge(prix_2023, on="code_commune", how="left")
communes["evolution_1an_pct"] = (
    (communes["commune_prix_m2_2024"] - communes["commune_prix_m2_2023"])
    / communes["commune_prix_m2_2023"] * 100
).round(1)

print(f"   -> {len(communes):,} communes avec stats DVF")

# ── 4. MERGE INSEE ────────────────────────────────────────────
ENRICH_COLS = [
    "code_commune", "population_2023", "evolution_pop_5_ans", "evolution_pop_10_ans",
    "revenu_median", "taux_pauvrete", "nb_equipements_total",
    "equipements_par_1000_habitants",
    "nb_equipements_dom_C",   # enseignement
    "nb_equipements_dom_D",   # sante
    "nb_equipements_dom_B",   # commerces
    "taux_cambriolages", "taux_vols_total", "taux_violences_total",
]
communes = communes.merge(
    comm_feats[[c for c in ENRICH_COLS if c in comm_feats.columns]],
    on="code_commune", how="left"
)

# ── 5. DISTANCE GARE (BallTree haversine) ─────────────────────
print("\n[4/6] Calcul distance gare (BallTree)...")
gares_coords = np.radians(gares_voy[["Y_WGS84", "X_WGS84"]].values)
tree = BallTree(gares_coords, metric="haversine")

mask_valid   = communes["latitude"].notna() & communes["longitude"].notna()
comm_coords  = np.radians(communes.loc[mask_valid, ["latitude", "longitude"]].values)
distances, _ = tree.query(comm_coords, k=1)
distances_km = distances[:, 0] * 6371.0

communes.loc[mask_valid, "distance_gare_km"] = distances_km.round(1)
communes["gare_moins_5km"]  = (communes["distance_gare_km"] < 5).astype(float)
communes["gare_moins_10km"] = (communes["distance_gare_km"] < 10).astype(float)
print(f"   -> Distance calculee pour {mask_valid.sum():,} communes")

# ── 6. SCORE ATTRACTIVITE ─────────────────────────────────────
print("\n[5/6] Calcul score d'attractivite...")

def percentile_score(serie, inverse=False):
    ranks = serie.rank(pct=True, na_option="keep") * 100
    return (100 - ranks) if inverse else ranks

# Immobilier (25%) : prix abordable (60%) + evolution raisonnable (40%)
communes["_score_prix"] = percentile_score(communes["commune_prix_m2"], inverse=True)
evol_cap = communes["evolution_5ans_pct"].clip(-10, 50)
communes["_score_evol"] = percentile_score(evol_cap)
communes["score_immobilier"] = (0.6 * communes["_score_prix"] + 0.4 * communes["_score_evol"]).round(1)

# Dynamisme (20%)
communes["score_dynamisme"] = percentile_score(communes["evolution_pop_5_ans"].fillna(0)).round(1)

# Revenus (20%)
communes["score_revenus"] = percentile_score(communes["revenu_median"].fillna(communes["revenu_median"].median())).round(1)

# Equipements (15%)
communes["score_equipements"] = percentile_score(communes["equipements_par_1000_habitants"].fillna(0)).round(1)

# Securite (10%)
crime = (communes["taux_cambriolages"].fillna(0)
       + communes["taux_vols_total"].fillna(0)
       + communes["taux_violences_total"].fillna(0))
communes["score_securite"] = percentile_score(crime, inverse=True).round(1)

# Transport (10%)
communes["score_transport"] = percentile_score(
    communes["distance_gare_km"].fillna(50), inverse=True
).round(1)

# Score global
communes["score_attractivite"] = (
    0.25 * communes["score_immobilier"] +
    0.20 * communes["score_dynamisme"]  +
    0.20 * communes["score_revenus"]    +
    0.15 * communes["score_equipements"]+
    0.10 * communes["score_securite"]   +
    0.10 * communes["score_transport"]
).round(1)

communes = communes.drop(columns=[c for c in communes.columns if c.startswith("_")])
print(f"   -> Score moyen   : {communes['score_attractivite'].mean():.1f}/100")
print(f"   -> Score median  : {communes['score_attractivite'].median():.1f}/100")

# ── 7. SAUVEGARDE ─────────────────────────────────────────────
print("\n[6/6] Sauvegarde des fichiers...")

# communes_streamlit.csv
communes.to_csv(os.path.join(OUT, "communes_streamlit.csv"), index=False)
print(f"   OK communes_streamlit.csv  ({len(communes):,} lignes, {len(communes.columns)} colonnes)")

# evolution_prix_communes.csv
print("   Calcul evolution par commune x annee...")
evol_rows = []
for annee, grp in dvf.groupby("annee"):
    s_t = (grp.groupby("code_commune")["prix_m2"]
              .agg(prix_m2_median_tous="median", nb_transactions_tous="count")
              .reset_index())
    s_m = (grp[grp["is_maison"]==1].groupby("code_commune")["prix_m2"]
              .agg(prix_m2_median_maison="median", nb_transactions_maison="count")
              .reset_index())
    s_a = (grp[grp["is_maison"]==0].groupby("code_commune")["prix_m2"]
              .agg(prix_m2_median_appart="median", nb_transactions_appart="count")
              .reset_index())
    merged = s_t.merge(s_m, on="code_commune", how="outer").merge(s_a, on="code_commune", how="outer")
    merged["annee"] = annee
    evol_rows.append(merged)

evolution = pd.concat(evol_rows, ignore_index=True)
evolution = evolution.merge(
    communes[["code_commune", "nom_commune", "code_departement"]],
    on="code_commune", how="left"
)
# Garder seulement communes avec >= 5 transactions / an
evolution = evolution[evolution["nb_transactions_tous"].fillna(0) >= 5]
evolution.to_csv(os.path.join(OUT, "evolution_prix_communes.csv"), index=False)
print(f"   OK evolution_prix_communes.csv  ({len(evolution):,} lignes)")

# carte_prix_departements.csv
dept_rows = []
for annee, grp in dvf.groupby("annee"):
    s_t = (grp.groupby("code_departement")["prix_m2"]
              .agg(prix_m2_median_tous="median", nb_transactions="count")
              .reset_index())
    s_m = (grp[grp["is_maison"]==1].groupby("code_departement")["prix_m2"]
              .median().rename("prix_m2_median_maison").reset_index())
    s_a = (grp[grp["is_maison"]==0].groupby("code_departement")["prix_m2"]
              .median().rename("prix_m2_median_appart").reset_index())
    merged = s_t.merge(s_m, on="code_departement", how="outer").merge(s_a, on="code_departement", how="outer")
    merged["annee"] = annee
    dept_rows.append(merged)

carte = pd.concat(dept_rows, ignore_index=True)
carte.to_csv(os.path.join(OUT, "carte_prix_departements.csv"), index=False)
print(f"   OK carte_prix_departements.csv  ({len(carte):,} lignes)")

# GeoJSON departements
print("\n   Telechargement GeoJSON departements France...")
GEOJSON_URL = ("https://raw.githubusercontent.com/gregoiredavid/"
               "france-geojson/master/departements-version-simplifiee.geojson")
geojson_path = os.path.join(OUT, "departements.geojson")
try:
    r = requests.get(GEOJSON_URL, timeout=30)
    with open(geojson_path, "wb") as f:
        f.write(r.content)
    size_kb = os.path.getsize(geojson_path) // 1024
    print(f"   OK departements.geojson  ({size_kb} Ko)")
except Exception as e:
    print(f"   ERREUR telechargement : {e}")
    print("   -> Telecharger manuellement depuis :")
    print("      https://github.com/gregoiredavid/france-geojson")

# Resume
print("\n" + "=" * 60)
print("  DONE - Fichiers dans :", OUT)
print("=" * 60)
for f in sorted(os.listdir(OUT)):
    size = os.path.getsize(os.path.join(OUT, f)) // 1024
    print(f"  {f:<45} {size:>6} Ko")
print("\nProchaine etape :")
print("  cd app && streamlit run app.py")
