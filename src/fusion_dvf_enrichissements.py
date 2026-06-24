from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import BallTree


warnings.filterwarnings("ignore")


# ============================================================
# FUSION DVF + ENRICHISSEMENTS + CREATION DES FICHIERS ML
# ============================================================
#
# Ce fichier vient APRES :
# - Exploration 5 fichiers.ipynb
# - Nettoyage 5 fichiers enrichissement.ipynb
#
# Entrees :
# - dvf_final_2020_2025.csv
# - features_communes_clean.csv
# - liste-des-gares.csv
#
# Sorties :
# - dvf_model_ready_enriched.csv
# - X_train_enriched.csv
# - X_test_enriched.csv
# - y_train_enriched.csv
# - y_test_enriched.csv
#
# Idee :
# 1. Nettoyer DVF.
# 2. Fusionner les variables communales avec code_commune.
# 3. Ajouter distance_gare_plus_proche_km via GPS.
# 4. Split train/test.
# 5. Calculer commune_prix_m2 uniquement sur train.
# ============================================================


DOSSIER = Path(r"C:\Users\a\Desktop\Projet Immo")

FICHIER_DVF = DOSSIER / "dvf_final_2020_2025.csv"
FICHIER_FEATURES = DOSSIER / "features_communes_clean.csv"
FICHIER_GARES = DOSSIER / "liste-des-gares.csv"

SORTIE_DVF_ML = DOSSIER / "dvf_model_ready_enriched.csv"
SORTIE_X_TRAIN = DOSSIER / "X_train_enriched.csv"
SORTIE_X_TEST = DOSSIER / "X_test_enriched.csv"
SORTIE_Y_TRAIN = DOSSIER / "y_train_enriched.csv"
SORTIE_Y_TEST = DOSSIER / "y_test_enriched.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.20


def titre(message):
    print("\n" + "=" * 100)
    print(message)
    print("=" * 100)


def sous_titre(message):
    print("\n" + "-" * 100)
    print(message)
    print("-" * 100)


def code_commune_5(series):
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def code_departement_numeric(series):
    return (
        series.astype(str)
        .str.replace("2A", "201", regex=False)
        .str.replace("2B", "202", regex=False)
        .astype(float)
    )


def afficher_resume(df, nom, n=5):
    print(f"\nResume : {nom}")
    print(f"Dimensions : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    print("\nColonnes :")
    print(list(df.columns))
    print("\nApercu :")
    print(df.head(n).to_string())
    print("\nValeurs manquantes principales (%) :")
    print((df.isna().mean() * 100).round(2).sort_values(ascending=False).head(20).to_string())


def charger_et_nettoyer_dvf():
    titre("1. CHARGEMENT ET NETTOYAGE DE DVF")

    print("On repart du fichier principal : dvf_final_2020_2025.csv")
    print("On garde les colonnes utiles pour la modelisation et la fusion.")

    colonnes = [
        "id_mutation",
        "date_mutation",
        "annee",
        "mois",
        "nature_mutation",
        "valeur_fonciere",
        "surface_reelle_bati",
        "prix_m2",
        "type_local",
        "nombre_pieces_principales",
        "surface_terrain",
        "code_departement",
        "code_commune",
        "nom_commune",
        "longitude",
        "latitude",
    ]

    debut = time.time()
    df = pd.read_csv(FICHIER_DVF, usecols=colonnes, dtype={"code_commune": str}, low_memory=False)
    print(f"Chargement termine en {(time.time() - debut):.2f} secondes")
    afficher_resume(df, "DVF brut")

    sous_titre("Etape 1 : filtrer les ventes de maisons et appartements")
    lignes_depart = len(df)
    df = df[df["nature_mutation"].isin(["Vente", "Vente en l'état futur d'achèvement"])].copy()
    df = df[df["type_local"].isin(["Maison", "Appartement"])].copy()
    print(f"Lignes avant filtre : {lignes_depart:,}")
    print(f"Lignes apres filtre : {len(df):,}")

    sous_titre("Etape 2 : convertir les colonnes numeriques")
    colonnes_numeriques = [
        "valeur_fonciere",
        "surface_reelle_bati",
        "prix_m2",
        "nombre_pieces_principales",
        "surface_terrain",
        "longitude",
        "latitude",
    ]
    for col in colonnes_numeriques:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["code_commune"] = code_commune_5(df["code_commune"])
    df["code_departement"] = code_departement_numeric(df["code_departement"])

    sous_titre("Etape 3 : supprimer les lignes inutilisables")
    avant = len(df)
    df = df.dropna(
        subset=[
            "valeur_fonciere",
            "surface_reelle_bati",
            "prix_m2",
            "nombre_pieces_principales",
            "longitude",
            "latitude",
            "code_commune",
        ]
    )
    print(f"Lignes supprimees pour valeurs manquantes essentielles : {avant - len(df):,}")

    sous_titre("Etape 4 : appliquer des filtres metier raisonnables")
    print("Ces filtres retirent les cas extremes ou atypiques qui perturbent fortement les modeles.")
    avant = len(df)
    df = df[df["valeur_fonciere"].between(20_000, 2_000_000)]
    df = df[df["surface_reelle_bati"].between(10, 500)]
    df = df[df["prix_m2"].between(300, 20_000)]
    df = df[df["nombre_pieces_principales"].between(1, 15)]
    df["surface_terrain"] = df["surface_terrain"].fillna(0).clip(lower=0, upper=10_000)
    df = df[df["latitude"].between(41, 52) & df["longitude"].between(-6, 10)]
    print(f"Lignes avant filtres metier : {avant:,}")
    print(f"Lignes apres filtres metier : {len(df):,}")
    print(f"Lignes retirees : {avant - len(df):,}")

    sous_titre("Etape 5 : creer les variables de base")
    df["is_maison"] = (df["type_local"] == "Maison").astype(int)
    df["is_neuf"] = (df["nature_mutation"] == "Vente en l'état futur d'achèvement").astype(int)
    df["anciennete_mois"] = (2026 - df["annee"]) * 12 + (5 - df["mois"])
    df["surface_par_piece"] = df["surface_reelle_bati"] / df["nombre_pieces_principales"]
    df["densite_pieces"] = df["nombre_pieces_principales"] / df["surface_reelle_bati"]
    df["prix_log"] = np.log1p(df["valeur_fonciere"])
    df["surface_log"] = np.log1p(df["surface_reelle_bati"])

    afficher_resume(df, "DVF nettoye avec variables de base")
    return df


def fusionner_features_communes(df):
    titre("2. FUSION AVEC LES FEATURES COMMUNALES")

    print("On utilise features_communes_clean.csv cree par le notebook de nettoyage des 5 fichiers.")
    features = pd.read_csv(FICHIER_FEATURES, dtype={"code_commune": str}, low_memory=False)
    features["code_commune"] = code_commune_5(features["code_commune"])

    afficher_resume(features, "features communales")

    avant_cols = df.shape[1]
    df = df.merge(features, on="code_commune", how="left")

    print(f"\nColonnes avant fusion : {avant_cols}")
    print(f"Colonnes apres fusion : {df.shape[1]}")
    print(f"Lignes apres fusion   : {df.shape[0]:,}")

    afficher_resume(df, "DVF + features communales", n=3)
    return df


def ajouter_distance_gare(df):
    titre("3. AJOUT DE LA DISTANCE A LA GARE LA PLUS PROCHE")

    print("Methode propre : calcul GPS entre chaque bien DVF et les gares voyageurs.")
    print("On n'utilise pas le nom de commune, car les noms peuvent varier selon les fichiers.")

    gares = pd.read_csv(FICHIER_GARES, sep=";", low_memory=False)
    gares["X_WGS84"] = pd.to_numeric(gares["X_WGS84"], errors="coerce")
    gares["Y_WGS84"] = pd.to_numeric(gares["Y_WGS84"], errors="coerce")

    gares = gares[
        (gares["VOYAGEURS"] == "O")
        & gares["X_WGS84"].between(-6, 10)
        & gares["Y_WGS84"].between(41, 52)
    ].copy()

    print(f"Gares voyageurs retenues : {len(gares):,}")
    print(gares[["LIBELLE", "COMMUNE", "X_WGS84", "Y_WGS84"]].head().to_string())

    coords_gares = np.radians(gares[["Y_WGS84", "X_WGS84"]].values)
    tree = BallTree(coords_gares, metric="haversine")

    gps_ok = (
        df["latitude"].notna()
        & df["longitude"].notna()
        & df["latitude"].between(41, 52)
        & df["longitude"].between(-6, 10)
    )

    print(f"Biens avec GPS valides : {gps_ok.sum():,} / {len(df):,}")

    coords_biens = np.radians(df.loc[gps_ok, ["latitude", "longitude"]].values)
    distances_rad, _ = tree.query(coords_biens, k=1)
    distances_km = distances_rad.flatten() * 6371.0088

    df["distance_gare_plus_proche_km"] = np.nan
    df.loc[gps_ok, "distance_gare_plus_proche_km"] = distances_km
    df["gare_moins_5km"] = (df["distance_gare_plus_proche_km"] <= 5).astype(int)
    df["gare_moins_10km"] = (df["distance_gare_plus_proche_km"] <= 10).astype(int)

    print("\nStatistiques distance gare :")
    print(df["distance_gare_plus_proche_km"].describe().to_string())
    print("\nExemples :")
    print(df[["nom_commune", "latitude", "longitude", "distance_gare_plus_proche_km", "gare_moins_5km", "gare_moins_10km"]].head().to_string())
    return df


def imputer_valeurs_manquantes(df):
    titre("4. IMPUTATION DES VALEURS MANQUANTES")

    print("Pour les variables numeriques, on remplace les valeurs manquantes par la mediane.")
    print("C'est simple et robuste pour une premiere version.")

    colonnes_num = df.select_dtypes(include=[np.number]).columns.tolist()
    missing_avant = df[colonnes_num].isna().sum().sum()

    for col in colonnes_num:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    missing_apres = df[colonnes_num].isna().sum().sum()

    print(f"Valeurs manquantes numeriques avant : {missing_avant:,}")
    print(f"Valeurs manquantes numeriques apres : {missing_apres:,}")
    return df


def sauvegarder_dataset_ml(df):
    titre("5. SAUVEGARDE DU DATASET ML ENRICHI")

    print("On sauvegarde un fichier intermediaire propre avant split.")
    print("Ce fichier garde encore code_commune et prix_m2 pour calculer commune_prix_m2 proprement apres split.")

    df.to_csv(SORTIE_DVF_ML, index=False)

    print(f"Fichier sauvegarde : {SORTIE_DVF_ML}")
    print(f"Dimensions : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    return df


def creer_train_test(df):
    titre("6. SPLIT TRAIN/TEST ET CREATION DES FICHIERS ML")

    print("On fait le split avant de calculer commune_prix_m2.")
    print("Cela evite le data leakage : le test ne participe pas au calcul des moyennes communales.")

    train_df, test_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    print(f"Train : {train_df.shape[0]:,} lignes")
    print(f"Test  : {test_df.shape[0]:,} lignes")

    sous_titre("Calcul de commune_prix_m2 uniquement sur train")
    commune_stats = (
        train_df.groupby("code_commune")
        .agg(
            commune_prix_m2=("prix_m2", "median"),
            commune_volume=("prix_m2", "size"),
        )
        .reset_index()
    )

    fallback_prix_m2 = train_df["prix_m2"].median()
    print(f"Prix m2 median global train utilise en secours : {fallback_prix_m2:.2f}")

    train_df = train_df.merge(commune_stats, on="code_commune", how="left")
    test_df = test_df.merge(commune_stats, on="code_commune", how="left")

    train_df["commune_prix_m2"] = train_df["commune_prix_m2"].fillna(fallback_prix_m2)
    test_df["commune_prix_m2"] = test_df["commune_prix_m2"].fillna(fallback_prix_m2)
    train_df["commune_volume"] = train_df["commune_volume"].fillna(0)
    test_df["commune_volume"] = test_df["commune_volume"].fillna(0)

    cible = "valeur_fonciere"
    colonnes_a_retirer = [
        "id_mutation",
        "date_mutation",
        "nature_mutation",
        "type_local",
        "nom_commune",
        "code_commune",
        "prix_m2",
        "prix_log",
        cible,
    ]

    X_train = train_df.drop(columns=[c for c in colonnes_a_retirer if c in train_df.columns])
    X_test = test_df.drop(columns=[c for c in colonnes_a_retirer if c in test_df.columns])

    y_train = train_df[[cible]]
    y_test = test_df[[cible]]

    # On garde uniquement les colonnes numeriques pour les modeles.
    X_train = X_train.select_dtypes(include=[np.number])
    X_test = X_test[X_train.columns]

    # Securite finale : aucun NaN dans X.
    for col in X_train.columns:
        if X_train[col].isna().any():
            med = X_train[col].median()
            X_train[col] = X_train[col].fillna(med)
            X_test[col] = X_test[col].fillna(med)

    X_train.to_csv(SORTIE_X_TRAIN, index=False)
    X_test.to_csv(SORTIE_X_TEST, index=False)
    y_train.to_csv(SORTIE_Y_TRAIN, index=False)
    y_test.to_csv(SORTIE_Y_TEST, index=False)

    print("\nFichiers crees :")
    print(f"X_train : {X_train.shape} -> {SORTIE_X_TRAIN}")
    print(f"X_test  : {X_test.shape} -> {SORTIE_X_TEST}")
    print(f"y_train : {y_train.shape} -> {SORTIE_Y_TRAIN}")
    print(f"y_test  : {y_test.shape} -> {SORTIE_Y_TEST}")

    print("\nColonnes finales du modele :")
    for col in X_train.columns:
        print(f"- {col}")

    return X_train, X_test, y_train, y_test


def main():
    debut = time.time()

    titre("DEBUT FUSION DVF + ENRICHISSEMENTS")
    print(f"Dossier projet : {DOSSIER}")
    print("\nFichiers attendus :")
    for fichier in [FICHIER_DVF, FICHIER_FEATURES, FICHIER_GARES]:
        print(f"- {fichier.name} : {'OK' if fichier.exists() else 'MANQUANT'}")

    df = charger_et_nettoyer_dvf()
    df = fusionner_features_communes(df)
    df = ajouter_distance_gare(df)
    df = imputer_valeurs_manquantes(df)
    sauvegarder_dataset_ml(df)
    creer_train_test(df)

    titre("FUSION TERMINEE")
    print(f"Temps total : {(time.time() - debut) / 60:.2f} minutes")
    print("Prochaine etape : relancer les modeles avec X_train_enriched et X_test_enriched.")


if __name__ == "__main__":
    main()
