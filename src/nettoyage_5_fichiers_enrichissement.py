from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree


warnings.filterwarnings("ignore")


# ============================================================
# NETTOYAGE DES 5 FICHIERS D'ENRICHISSEMENT
# ============================================================
#
# Ce fichier ne touche pas encore au fichier DVF.
#
# Objectif :
# - Nettoyer les 5 fichiers externes trouves pour le projet.
# - Transformer chaque fichier en variables simples par commune.
# - Creer un fichier final : features_communes_clean.csv
#
# Les 5 sources :
# 1. Population historique  -> demographie
# 2. Filosofi INSEE         -> economie / revenus / menages
# 3. BPE equipements        -> services / commerces / sante / education
# 4. Criminalite            -> securite
# 5. Liste des gares        -> transports
#
# Sorties :
# - features_population_clean.csv
# - features_filosofi_clean.csv
# - features_bpe_clean.csv
# - features_criminalite_clean.csv
# - features_gares_clean.csv
# - features_communes_clean.csv
# ============================================================


DOSSIER = Path(r"C:\Users\a\Desktop\Projet Immo")

FICHIER_POPULATION = DOSSIER / "DS_POPULATIONS_HISTORIQUES_data.csv"
FICHIER_FILOSOFI = DOSSIER / "DS_FILOSOFI_CC_2021_data.csv"
FICHIER_BPE = DOSSIER / "DS_BPE_2024_data.csv"
FICHIER_CRIMINALITE = DOSSIER / "donnee-data.gouv-2025-geographie2025-produit-le2026-02-03.csv.gz"
FICHIER_GARES = DOSSIER / "liste-des-gares.csv"

SORTIE_POPULATION = DOSSIER / "features_population_clean.csv"
SORTIE_FILOSOFI = DOSSIER / "features_filosofi_clean.csv"
SORTIE_BPE = DOSSIER / "features_bpe_clean.csv"
SORTIE_CRIMINALITE = DOSSIER / "features_criminalite_clean.csv"
SORTIE_GARES = DOSSIER / "features_gares_clean.csv"
SORTIE_FINALE = DOSSIER / "features_communes_clean.csv"


def titre(message):
    print("\n" + "=" * 100)
    print(message)
    print("=" * 100)


def sous_titre(message):
    print("\n" + "-" * 100)
    print(message)
    print("-" * 100)


def code_commune_5(series):
    """
    Transforme un code commune en texte sur 5 caracteres.

    Exemple :
    1001  -> 01001
    75056 -> 75056

    C'est indispensable pour faire des fusions fiables avec DVF.
    """
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def convertir_float_fr(series):
    """
    Convertit les nombres avec virgule francaise en float.

    Exemple :
    '7,9679210' devient 7.9679210
    """
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def afficher_resume(df, nom):
    print(f"\nResume {nom}")
    print(f"Dimensions : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    print("\nColonnes :")
    print(list(df.columns))
    print("\nApercu :")
    print(df.head().to_string())
    print("\nValeurs manquantes (%) :")
    print((df.isna().mean() * 100).round(2).sort_values(ascending=False).head(20).to_string())


def nettoyer_population():
    titre("1. NETTOYAGE POPULATION HISTORIQUE")

    print("Objectif : obtenir la population recente et son evolution par commune.")
    print("Colonnes utilisees : GEO, GEO_OBJECT, POPREF_MEASURE, TIME_PERIOD, OBS_VALUE.")

    df = pd.read_csv(
        FICHIER_POPULATION,
        sep=";",
        usecols=["GEO", "GEO_OBJECT", "POPREF_MEASURE", "TIME_PERIOD", "OBS_VALUE"],
        dtype={"GEO": str},
    )

    afficher_resume(df, "population brute")

    sous_titre("Etape 1 : garder uniquement les communes")
    df = df[df["GEO_OBJECT"] == "COM"].copy()
    print(f"Lignes apres filtre commune : {len(df):,}")

    sous_titre("Etape 2 : garder uniquement PMUN")
    print("PMUN = population municipale. C'est la population de reference la plus utile ici.")
    df = df[df["POPREF_MEASURE"] == "PMUN"].copy()
    print(f"Lignes apres filtre PMUN : {len(df):,}")

    sous_titre("Etape 3 : garder quelques annees utiles")
    annees_utiles = [2013, 2018, 2020, 2023]
    df = df[df["TIME_PERIOD"].isin(annees_utiles)].copy()
    print(f"Annees conservees : {annees_utiles}")

    sous_titre("Etape 4 : passer du format long au format large")
    df["code_commune"] = code_commune_5(df["GEO"])

    pop = (
        df.pivot_table(
            index="code_commune",
            columns="TIME_PERIOD",
            values="OBS_VALUE",
            aggfunc="first",
        )
        .rename(
            columns={
                2013: "population_2013",
                2018: "population_2018",
                2020: "population_2020",
                2023: "population_2023",
            }
        )
        .reset_index()
    )

    sous_titre("Etape 5 : creer les evolutions de population")
    pop["evolution_pop_5_ans"] = (
        (pop["population_2023"] - pop["population_2018"])
        / pop["population_2018"].replace(0, np.nan)
    )
    pop["evolution_pop_10_ans"] = (
        (pop["population_2023"] - pop["population_2013"])
        / pop["population_2013"].replace(0, np.nan)
    )

    afficher_resume(pop, "population nettoyee")
    pop.to_csv(SORTIE_POPULATION, index=False)
    print(f"\nFichier sauvegarde : {SORTIE_POPULATION}")
    return pop


def nettoyer_filosofi():
    titre("2. NETTOYAGE FILOSOFI INSEE")

    print("Objectif : recuperer revenus, menages, pauvrete et inegalites par commune.")
    print("On garde seulement quelques indicateurs utiles pour eviter trop de colonnes.")

    indicateurs = {
        "MED_SL": "revenu_median",
        "NUM_HH": "nb_menages",
        "NUM_PER": "nb_personnes",
        "PR_MD60": "taux_pauvrete",
        "D1_SL": "niveau_vie_d1",
        "D9_SL": "niveau_vie_d9",
        "IR_D9_D1_SL": "inegalite_d9_d1",
    }

    df = pd.read_csv(
        FICHIER_FILOSOFI,
        sep=";",
        usecols=["GEO", "GEO_OBJECT", "FILOSOFI_MEASURE", "OBS_VALUE"],
        dtype={"GEO": str},
    )

    afficher_resume(df, "Filosofi brut")

    sous_titre("Etape 1 : garder uniquement les communes")
    df = df[df["GEO_OBJECT"] == "COM"].copy()
    print(f"Lignes apres filtre commune : {len(df):,}")

    sous_titre("Etape 2 : garder seulement les indicateurs selectionnes")
    print("Indicateurs conserves :")
    for code, nom in indicateurs.items():
        print(f"- {code} -> {nom}")

    df = df[df["FILOSOFI_MEASURE"].isin(indicateurs.keys())].copy()
    df["code_commune"] = code_commune_5(df["GEO"])

    sous_titre("Etape 3 : passer du format long au format large")
    filo = (
        df.pivot_table(
            index="code_commune",
            columns="FILOSOFI_MEASURE",
            values="OBS_VALUE",
            aggfunc="first",
        )
        .rename(columns=indicateurs)
        .reset_index()
    )

    afficher_resume(filo, "Filosofi nettoye")
    filo.to_csv(SORTIE_FILOSOFI, index=False)
    print(f"\nFichier sauvegarde : {SORTIE_FILOSOFI}")
    return filo


def nettoyer_bpe():
    titre("3. NETTOYAGE BPE EQUIPEMENTS")

    print("Objectif : compter les equipements par commune.")
    print("On regroupe par FACILITY_DOM, c'est-a-dire par grande famille d'equipements.")

    df = pd.read_csv(
        FICHIER_BPE,
        sep=";",
        usecols=["GEO", "GEO_OBJECT", "FACILITY_DOM", "OBS_VALUE"],
        dtype={"GEO": str},
    )

    afficher_resume(df, "BPE brut")

    sous_titre("Etape 1 : garder uniquement les communes")
    df = df[df["GEO_OBJECT"] == "COM"].copy()
    df["code_commune"] = code_commune_5(df["GEO"])
    print(f"Lignes apres filtre commune : {len(df):,}")

    sous_titre("Etape 2 : sommer les equipements par commune et domaine")
    bpe = (
        df.groupby(["code_commune", "FACILITY_DOM"], as_index=False)["OBS_VALUE"]
        .sum()
        .pivot(index="code_commune", columns="FACILITY_DOM", values="OBS_VALUE")
        .fillna(0)
    )

    bpe.columns = [f"nb_equipements_dom_{col}" for col in bpe.columns]
    bpe = bpe.reset_index()

    sous_titre("Etape 3 : creer le nombre total d'equipements")
    cols_equipements = [c for c in bpe.columns if c.startswith("nb_equipements_dom_")]
    bpe["nb_equipements_total"] = bpe[cols_equipements].sum(axis=1)

    afficher_resume(bpe, "BPE nettoye")
    bpe.to_csv(SORTIE_BPE, index=False)
    print(f"\nFichier sauvegarde : {SORTIE_BPE}")
    return bpe


def nettoyer_criminalite():
    titre("4. NETTOYAGE CRIMINALITE")

    print("Objectif : creer des taux de criminalite par commune.")
    print("On utilise 2024 car c'est une annee recente complete.")
    print("On utilise taux_pour_mille, sinon complement_info_taux si le taux direct est absent.")

    df = pd.read_csv(
        FICHIER_CRIMINALITE,
        sep=";",
        compression="gzip",
        usecols=["CODGEO_2025", "annee", "indicateur", "taux_pour_mille", "complement_info_taux"],
        dtype={"CODGEO_2025": str},
        low_memory=False,
    )

    afficher_resume(df, "criminalite brute")

    sous_titre("Etape 1 : garder uniquement l'annee 2024")
    df = df[df["annee"] == 2024].copy()
    print(f"Lignes 2024 : {len(df):,}")

    sous_titre("Etape 2 : creer le taux final")
    df["code_commune"] = code_commune_5(df["CODGEO_2025"])
    taux_direct = convertir_float_fr(df["taux_pour_mille"])
    taux_complement = convertir_float_fr(df["complement_info_taux"])
    df["taux_final"] = taux_direct.fillna(taux_complement)

    sous_titre("Etape 3 : renommer les indicateurs en variables ML")
    mapping = {
        "Cambriolages de logement": "taux_cambriolages",
        "Destructions et dégradations volontaires": "taux_degradations",
        "Escroqueries et fraudes aux moyens de paiement": "taux_escroqueries",
        "Trafic de stupéfiants": "taux_trafic_stupefiants",
        "Usage de stupéfiants": "taux_usage_stupefiants",
        "Violences physiques hors cadre familial": "taux_violences_hors_famille",
        "Violences physiques intrafamiliales": "taux_violences_intrafamiliales",
        "Violences sexuelles": "taux_violences_sexuelles",
        "Vols avec armes": "taux_vols_armes",
        "Vols d'accessoires sur véhicules": "taux_vols_accessoires_vehicules",
        "Vols dans les véhicules": "taux_vols_dans_vehicules",
        "Vols de véhicule": "taux_vols_vehicule",
        "Vols sans violence contre des personnes": "taux_vols_sans_violence",
        "Vols violents sans arme": "taux_vols_violents",
    }
    df["variable"] = df["indicateur"].map(mapping)
    df = df[df["variable"].notna()].copy()

    sous_titre("Etape 4 : passer du format long au format large")
    crime = (
        df.pivot_table(
            index="code_commune",
            columns="variable",
            values="taux_final",
            aggfunc="mean",
        )
        .reset_index()
    )

    sous_titre("Etape 5 : creer des indicateurs agreges")
    violence_cols = [
        "taux_violences_hors_famille",
        "taux_violences_intrafamiliales",
        "taux_violences_sexuelles",
    ]
    vols_cols = [
        "taux_vols_armes",
        "taux_vols_accessoires_vehicules",
        "taux_vols_dans_vehicules",
        "taux_vols_vehicule",
        "taux_vols_sans_violence",
        "taux_vols_violents",
    ]
    stup_cols = ["taux_trafic_stupefiants", "taux_usage_stupefiants"]

    for col in violence_cols + vols_cols + stup_cols:
        if col not in crime.columns:
            crime[col] = np.nan

    crime["taux_violences_total"] = crime[violence_cols].sum(axis=1, min_count=1)
    crime["taux_vols_total"] = crime[vols_cols].sum(axis=1, min_count=1)
    crime["taux_stupefiants_total"] = crime[stup_cols].sum(axis=1, min_count=1)

    afficher_resume(crime, "criminalite nettoyee")
    crime.to_csv(SORTIE_CRIMINALITE, index=False)
    print(f"\nFichier sauvegarde : {SORTIE_CRIMINALITE}")
    return crime


def nettoyer_gares():
    titre("5. NETTOYAGE LISTE DES GARES")

    print("Objectif : creer des variables transport par commune.")
    print("Ici on cree une version simple par commune : nombre de gares voyageurs.")
    print("La distance a la gare la plus proche sera calculee plus tard avec DVF, car il faut les GPS des biens.")

    df = pd.read_csv(FICHIER_GARES, sep=";", low_memory=False)
    afficher_resume(df, "gares brutes")

    sous_titre("Etape 1 : convertir les coordonnees GPS")
    df["X_WGS84"] = pd.to_numeric(df["X_WGS84"], errors="coerce")
    df["Y_WGS84"] = pd.to_numeric(df["Y_WGS84"], errors="coerce")

    sous_titre("Etape 2 : garder les gares avec voyageurs et GPS valides")
    gares_voyageurs = df[
        (df["VOYAGEURS"] == "O")
        & df["X_WGS84"].between(-6, 10)
        & df["Y_WGS84"].between(41, 52)
    ].copy()
    print(f"Gares voyageurs retenues : {len(gares_voyageurs):,}")

    sous_titre("Etape 3 : creer des features simples par nom de commune")
    print("Attention : cette sortie par nom de commune sert surtout a la dataviz.")
    print("Pour le ML, la meilleure variable sera distance_gare_plus_proche_km calculee avec les GPS DVF.")

    gares = (
        gares_voyageurs.groupby(["COMMUNE", "DEPARTEMEN"], as_index=False)
        .agg(
            nb_gares_voyageurs=("LIBELLE", "count"),
            longitude_gare_moyenne=("X_WGS84", "mean"),
            latitude_gare_moyenne=("Y_WGS84", "mean"),
        )
    )
    gares["presence_gare_voyageurs"] = (gares["nb_gares_voyageurs"] > 0).astype(int)

    afficher_resume(gares, "gares nettoyees")
    gares.to_csv(SORTIE_GARES, index=False)
    print(f"\nFichier sauvegarde : {SORTIE_GARES}")
    return gares


def calculer_distance_gare_exemple():
    titre("BONUS : FONCTION POUR CALCULER LA DISTANCE A LA GARE LA PLUS PROCHE")

    print("Cette fonction ne cree pas encore le fichier final, car elle doit etre appliquee au fichier DVF.")
    print("Elle montre comment on calculera distance_gare_plus_proche_km plus tard.")

    code = r'''
def ajouter_distance_gare_plus_proche(df_dvf, fichier_gares):
    gares = pd.read_csv(fichier_gares, sep=";", low_memory=False)
    gares["X_WGS84"] = pd.to_numeric(gares["X_WGS84"], errors="coerce")
    gares["Y_WGS84"] = pd.to_numeric(gares["Y_WGS84"], errors="coerce")

    gares = gares[
        (gares["VOYAGEURS"] == "O")
        & gares["X_WGS84"].between(-6, 10)
        & gares["Y_WGS84"].between(41, 52)
    ].copy()

    coords_gares = np.radians(gares[["Y_WGS84", "X_WGS84"]].values)
    tree = BallTree(coords_gares, metric="haversine")

    gps_ok = (
        df_dvf["latitude"].notna()
        & df_dvf["longitude"].notna()
        & df_dvf["latitude"].between(41, 52)
        & df_dvf["longitude"].between(-6, 10)
    )

    df_dvf["distance_gare_plus_proche_km"] = np.nan
    coords_biens = np.radians(df_dvf.loc[gps_ok, ["latitude", "longitude"]].values)
    distances_rad, _ = tree.query(coords_biens, k=1)
    distances_km = distances_rad.flatten() * 6371.0088

    df_dvf.loc[gps_ok, "distance_gare_plus_proche_km"] = distances_km
    df_dvf["gare_moins_5km"] = (df_dvf["distance_gare_plus_proche_km"] <= 5).astype(int)
    df_dvf["gare_moins_10km"] = (df_dvf["distance_gare_plus_proche_km"] <= 10).astype(int)
    return df_dvf
'''
    print(code)


def fusionner_features(pop, filo, bpe, crime):
    titre("6. FUSION DES FEATURES COMMUNALES")

    print("On fusionne population + Filosofi + BPE + criminalite avec la cle code_commune.")
    print("Les gares ne sont pas fusionnees ici, car le fichier gares n'a pas de code commune fiable.")
    print("Pour les gares, on utilisera la distance GPS au moment de fusionner avec DVF.")

    features = pop.merge(filo, on="code_commune", how="outer")
    features = features.merge(bpe, on="code_commune", how="outer")
    features = features.merge(crime, on="code_commune", how="outer")

    sous_titre("Creation d'un ratio utile : equipements par 1000 habitants")
    features["equipements_par_1000_habitants"] = (
        features["nb_equipements_total"] / features["population_2023"].replace(0, np.nan) * 1000
    )

    afficher_resume(features, "features communes finales")
    features.to_csv(SORTIE_FINALE, index=False)
    print(f"\nFichier final sauvegarde : {SORTIE_FINALE}")
    return features


def main():
    debut = time.time()

    titre("DEBUT DU NETTOYAGE DES 5 FICHIERS")
    print(f"Dossier projet : {DOSSIER}")
    print("\nFichiers attendus :")
    for fichier in [
        FICHIER_POPULATION,
        FICHIER_FILOSOFI,
        FICHIER_BPE,
        FICHIER_CRIMINALITE,
        FICHIER_GARES,
    ]:
        print(f"- {fichier.name} : {'OK' if fichier.exists() else 'MANQUANT'}")

    pop = nettoyer_population()
    filo = nettoyer_filosofi()
    bpe = nettoyer_bpe()
    crime = nettoyer_criminalite()
    nettoyer_gares()
    calculer_distance_gare_exemple()
    fusionner_features(pop, filo, bpe, crime)

    titre("NETTOYAGE TERMINE")
    print("Fichiers crees :")
    for sortie in [
        SORTIE_POPULATION,
        SORTIE_FILOSOFI,
        SORTIE_BPE,
        SORTIE_CRIMINALITE,
        SORTIE_GARES,
        SORTIE_FINALE,
    ]:
        print(f"- {sortie}")

    print(f"\nTemps total : {(time.time() - debut) / 60:.2f} minutes")


if __name__ == "__main__":
    main()
