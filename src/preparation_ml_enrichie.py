from pathlib import Path
import time

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


# ============================================================
# PREPARATION ML ENRICHIE
# ============================================================
#
# Objectif :
# - Charger le fichier DVF enrichi avec donnees communales + gares
# - Nettoyer les lignes pour la modelisation
# - Creer des variables utiles
# - Faire le split train/test
# - Calculer commune_prix_m2 uniquement sur le train
# - Exporter X_train / X_test / y_train / y_test enrichis
#
# Entree :
# - dvf_final_2020_2025_avec_enrichissements_gares.csv
#
# Sorties :
# - dvf_clean_model_ready_enriched.csv
# - X_train_enriched.csv
# - X_test_enriched.csv
# - y_train_enriched.csv
# - y_test_enriched.csv
# ============================================================


DOSSIER = Path(r"C:\Users\a\Desktop\Projet Immo")

FICHIER_ENTREE = DOSSIER / "dvf_final_2020_2025_avec_enrichissements_gares.csv"
FICHIER_ML_READY = DOSSIER / "dvf_clean_model_ready_enriched.csv"

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


def afficher_resume(df, nom, n=5):
    print(f"\nResume : {nom}")
    print(f"Dimensions : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    print("\nApercu :")
    print(df.head(n).to_string())
    print("\nValeurs manquantes principales (%) :")
    print((df.isna().mean() * 100).round(2).sort_values(ascending=False).head(25).to_string())


def code_commune_5(series):
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def code_departement_numeric(series):
    return (
        series.astype(str)
        .str.replace("2A", "201", regex=False)
        .str.replace("2B", "202", regex=False)
        .astype(float)
    )


def charger_donnees():
    titre("1. CHARGEMENT DU FICHIER ENRICHI")

    if not FICHIER_ENTREE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {FICHIER_ENTREE}")

    print(f"Fichier charge : {FICHIER_ENTREE}")
    print("Ce fichier contient DVF + population + revenus + equipements + criminalite + gares.")

    debut = time.time()
    df = pd.read_csv(
        FICHIER_ENTREE,
        dtype={"code_commune": str},
        low_memory=False,
    )
    print(f"Chargement termine en {(time.time() - debut) / 60:.2f} minutes")

    afficher_resume(df, "donnees enrichies brutes", n=3)
    return df


def nettoyer_dvf(df):
    titre("2. NETTOYAGE DES DONNEES IMMOBILIERES")

    print("On applique des filtres metier proches du travail de Carine, mais sur le fichier enrichi.")
    print("But : retirer les lignes inutilisables ou trop atypiques pour une premiere modelisation.")

    lignes_depart = len(df)

    sous_titre("2.1 Garder uniquement les ventes de maisons et appartements")
    df = df[df["nature_mutation"].isin(["Vente", "Vente en l'état futur d'achèvement"])].copy()
    df = df[df["type_local"].isin(["Maison", "Appartement"])].copy()
    print(f"Lignes apres filtre ventes / maisons-appartements : {len(df):,}")

    sous_titre("2.2 Conversion des variables numeriques")
    colonnes_numeriques = [
        "valeur_fonciere",
        "surface_reelle_bati",
        "prix_m2",
        "nombre_pieces_principales",
        "surface_terrain",
        "code_departement",
        "longitude",
        "latitude",
        "distance_gare_plus_proche_km",
    ]
    for col in colonnes_numeriques:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["code_commune"] = code_commune_5(df["code_commune"])
    df["code_departement"] = code_departement_numeric(df["code_departement"])

    sous_titre("2.3 Suppression des lignes avec informations essentielles manquantes")
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
    print(f"Lignes supprimees : {avant - len(df):,}")

    sous_titre("2.4 Filtres metier")
    print("Ces seuils retirent les biens extremes qui perturbent les modeles.")
    print("- valeur_fonciere entre 20 000 et 2 000 000 euros")
    print("- surface_reelle_bati entre 10 et 500 m2")
    print("- prix_m2 entre 300 et 20 000 euros/m2")
    print("- nombre_pieces_principales entre 1 et 15")
    print("- coordonnees GPS France metropolitaine approximative")

    avant = len(df)
    df = df[df["valeur_fonciere"].between(20_000, 2_000_000)]
    df = df[df["surface_reelle_bati"].between(10, 500)]
    df = df[df["prix_m2"].between(300, 20_000)]
    df = df[df["nombre_pieces_principales"].between(1, 15)]
    df["surface_terrain"] = df["surface_terrain"].fillna(0).clip(lower=0, upper=10_000)
    df = df[df["latitude"].between(41, 52) & df["longitude"].between(-6, 10)]

    print(f"Lignes avant filtres metier : {avant:,}")
    print(f"Lignes apres filtres metier : {len(df):,}")
    print(f"Lignes retirees par filtres : {avant - len(df):,}")

    titre("BILAN NETTOYAGE")
    print(f"Lignes au depart : {lignes_depart:,}")
    print(f"Lignes conservees : {len(df):,}")
    print(f"Lignes supprimees au total : {lignes_depart - len(df):,}")

    afficher_resume(df, "donnees apres nettoyage", n=3)
    return df


def creer_variables(df):
    titre("3. CREATION DES VARIABLES ML")

    print("On cree les variables de base deja utilisees dans le projet, plus quelques variables simples.")

    df["is_maison"] = (df["type_local"] == "Maison").astype(int)
    df["is_neuf"] = (df["nature_mutation"] == "Vente en l'état futur d'achèvement").astype(int)

    # Anciennete par rapport a mai 2026.
    df["anciennete_mois"] = (2026 - df["annee"]) * 12 + (5 - df["mois"])

    # Variables de surface.
    df["surface_par_piece"] = df["surface_reelle_bati"] / df["nombre_pieces_principales"]
    df["densite_pieces"] = df["nombre_pieces_principales"] / df["surface_reelle_bati"]
    df["surface_log"] = np.log1p(df["surface_reelle_bati"])

    # Variables gares deja calculees dans l'etape precedente.
    if "distance_gare_plus_proche_km" in df.columns:
        df["distance_gare_plus_proche_km"] = pd.to_numeric(
            df["distance_gare_plus_proche_km"],
            errors="coerce",
        )
        df["gare_moins_5km"] = (df["distance_gare_plus_proche_km"] <= 5).astype(int)
        df["gare_moins_10km"] = (df["distance_gare_plus_proche_km"] <= 10).astype(int)

    print("\nVariables creees :")
    print("- is_maison")
    print("- is_neuf")
    print("- anciennete_mois")
    print("- surface_par_piece")
    print("- densite_pieces")
    print("- surface_log")
    print("- gare_moins_5km")
    print("- gare_moins_10km")

    afficher_resume(
        df[
            [
                "valeur_fonciere",
                "surface_reelle_bati",
                "nombre_pieces_principales",
                "is_maison",
                "is_neuf",
                "anciennete_mois",
                "surface_par_piece",
                "distance_gare_plus_proche_km",
                "gare_moins_5km",
                "gare_moins_10km",
            ]
        ],
        "variables creees",
    )

    return df


def choisir_colonnes_modelisation(df):
    titre("4. SELECTION DES COLONNES POUR LA MODELISATION")

    print("On garde seulement des variables numeriques exploitables par les modeles.")
    print("On garde code_commune temporairement pour calculer commune_prix_m2 apres split.")

    colonnes_base = [
        "surface_reelle_bati",
        "nombre_pieces_principales",
        "surface_terrain",
        "annee",
        "mois",
        "code_departement",
        "longitude",
        "latitude",
        "is_maison",
        "is_neuf",
        "anciennete_mois",
        "surface_par_piece",
        "densite_pieces",
        "surface_log",
    ]

    colonnes_enrichissement = [
        "population_2023",
        "evolution_pop_5_ans",
        "evolution_pop_10_ans",
        "revenu_median",
        "nb_menages",
        "nb_personnes",
        "nb_equipements_dom_A",
        "nb_equipements_dom_B",
        "nb_equipements_dom_C",
        "nb_equipements_dom_D",
        "nb_equipements_dom_E",
        "nb_equipements_dom_F",
        "nb_equipements_dom_G",
        "nb_equipements_dom__T",
        "nb_equipements_total",
        "equipements_par_1000_habitants",
        "taux_cambriolages",
        "taux_degradations",
        "taux_escroqueries",
        "taux_violences_total",
        "taux_vols_total",
        "taux_stupefiants_total",
        "distance_gare_plus_proche_km",
        "gare_moins_5km",
        "gare_moins_10km",
    ]

    # Variables Filosofi tres manquantes.
    # On ne les met pas dans la premiere version ML pour eviter trop d'imputation.
    colonnes_trop_manquantes = [
        "niveau_vie_d1",
        "niveau_vie_d9",
        "inegalite_d9_d1",
        "taux_pauvrete",
    ]

    colonnes_utiles = [
        col for col in colonnes_base + colonnes_enrichissement
        if col in df.columns
    ]

    colonnes_finales = ["code_commune", "prix_m2", "valeur_fonciere"] + colonnes_utiles
    df_ml = df[colonnes_finales].copy()

    print(f"Nombre de colonnes selectionnees avant commune_prix_m2 : {len(df_ml.columns)}")
    print("\nColonnes retenues :")
    for col in df_ml.columns:
        print(f"- {col}")

    print("\nColonnes volontairement non retenues dans cette premiere version car trop manquantes :")
    for col in colonnes_trop_manquantes:
        print(f"- {col}")

    afficher_resume(df_ml, "dataset ML avant split", n=3)
    return df_ml


def split_et_commune_prix_m2(df_ml):
    titre("5. SPLIT TRAIN/TEST ET CALCUL PROPRE DE commune_prix_m2")

    print("Point important : on calcule commune_prix_m2 uniquement sur le train.")
    print("Cela evite que le jeu de test influence les variables d'entrainement.")

    train_df, test_df = train_test_split(
        df_ml,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    print(f"Train : {train_df.shape[0]:,} lignes")
    print(f"Test  : {test_df.shape[0]:,} lignes")

    sous_titre("Calcul des statistiques communales sur train")
    stats_commune = (
        train_df.groupby("code_commune")
        .agg(
            commune_prix_m2=("prix_m2", "median"),
            commune_volume=("prix_m2", "size"),
        )
        .reset_index()
    )

    prix_m2_global_train = train_df["prix_m2"].median()
    print(f"Nombre de communes dans train : {stats_commune.shape[0]:,}")
    print(f"Prix m2 median global train : {prix_m2_global_train:.2f}")

    train_df = train_df.merge(stats_commune, on="code_commune", how="left")
    test_df = test_df.merge(stats_commune, on="code_commune", how="left")

    train_df["commune_prix_m2"] = train_df["commune_prix_m2"].fillna(prix_m2_global_train)
    test_df["commune_prix_m2"] = test_df["commune_prix_m2"].fillna(prix_m2_global_train)

    train_df["commune_volume"] = train_df["commune_volume"].fillna(0)
    test_df["commune_volume"] = test_df["commune_volume"].fillna(0)

    print("\nApercu commune_prix_m2 :")
    print(train_df[["code_commune", "prix_m2", "commune_prix_m2", "commune_volume"]].head().to_string())

    return train_df, test_df


def imputer_et_exporter(train_df, test_df):
    titre("6. IMPUTATION ET EXPORT DES FICHIERS ML")

    cible = "valeur_fonciere"

    # Colonnes a retirer des X.
    colonnes_a_retirer = [
        "code_commune",
        "prix_m2",
        cible,
    ]

    X_train = train_df.drop(columns=colonnes_a_retirer)
    X_test = test_df.drop(columns=colonnes_a_retirer)
    y_train = train_df[[cible]]
    y_test = test_df[[cible]]

    # Garder uniquement numerique.
    X_train = X_train.select_dtypes(include=[np.number])
    X_test = X_test[X_train.columns]

    sous_titre("Imputation des valeurs manquantes")
    print("Pour chaque colonne, la mediane est calculee sur X_train puis appliquee a X_train et X_test.")

    missing_avant_train = X_train.isna().sum().sum()
    missing_avant_test = X_test.isna().sum().sum()

    for col in X_train.columns:
        if X_train[col].isna().any() or X_test[col].isna().any():
            mediane = X_train[col].median()
            X_train[col] = X_train[col].fillna(mediane)
            X_test[col] = X_test[col].fillna(mediane)

    missing_apres_train = X_train.isna().sum().sum()
    missing_apres_test = X_test.isna().sum().sum()

    print(f"NaN X_train avant : {missing_avant_train:,}")
    print(f"NaN X_train apres : {missing_apres_train:,}")
    print(f"NaN X_test avant  : {missing_avant_test:,}")
    print(f"NaN X_test apres  : {missing_apres_test:,}")

    sous_titre("Sauvegarde du dataset ML ready complet")
    df_ready = pd.concat(
        [
            pd.concat([X_train, y_train.reset_index(drop=True)], axis=1),
            pd.concat([X_test, y_test.reset_index(drop=True)], axis=1),
        ],
        axis=0,
        ignore_index=True,
    )
    df_ready.to_csv(FICHIER_ML_READY, index=False)
    print(f"Fichier ML complet sauvegarde : {FICHIER_ML_READY}")
    print(f"Dimensions : {df_ready.shape}")

    sous_titre("Sauvegarde X_train / X_test / y_train / y_test")
    X_train.to_csv(SORTIE_X_TRAIN, index=False)
    X_test.to_csv(SORTIE_X_TEST, index=False)
    y_train.to_csv(SORTIE_Y_TRAIN, index=False)
    y_test.to_csv(SORTIE_Y_TEST, index=False)

    print(f"X_train : {X_train.shape} -> {SORTIE_X_TRAIN}")
    print(f"X_test  : {X_test.shape} -> {SORTIE_X_TEST}")
    print(f"y_train : {y_train.shape} -> {SORTIE_Y_TRAIN}")
    print(f"y_test  : {y_test.shape} -> {SORTIE_Y_TEST}")

    print("\nColonnes finales de X_train :")
    for col in X_train.columns:
        print(f"- {col}")

    return X_train, X_test, y_train, y_test


def main():
    debut = time.time()

    titre("DEBUT PREPARATION ML ENRICHIE")
    print(f"Dossier projet : {DOSSIER}")
    print(f"Fichier entree : {FICHIER_ENTREE}")

    df = charger_donnees()
    df = nettoyer_dvf(df)
    df = creer_variables(df)
    df_ml = choisir_colonnes_modelisation(df)
    train_df, test_df = split_et_commune_prix_m2(df_ml)
    imputer_et_exporter(train_df, test_df)

    titre("PREPARATION ML TERMINEE")
    print(f"Temps total : {(time.time() - debut) / 60:.2f} minutes")
    print("Prochaine etape : relancer les modeles avec X_train_enriched.csv et X_test_enriched.csv.")


if __name__ == "__main__":
    main()
