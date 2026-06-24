from pathlib import Path
import time

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree


# ============================================================
# AJOUT DISTANCE GARE LA PLUS PROCHE
# ============================================================
#
# Objectif :
# - Charger dvf_final_2020_2025_avec_enrichissements.csv
# - Charger liste-des-gares.csv
# - Garder uniquement les gares voyageurs avec GPS valide
# - Pour chaque bien DVF, calculer la distance a la gare la plus proche
# - Sauvegarder dvf_final_2020_2025_avec_enrichissements_gares.csv
#
# Ce fichier ne fait PAS :
# - de nettoyage ML
# - de split train/test
# - de modelisation
# ============================================================


DOSSIER = Path(r"C:\Users\a\Desktop\Projet Immo")

FICHIER_DVF_ENRICHI = DOSSIER / "dvf_final_2020_2025_avec_enrichissements.csv"
FICHIER_GARES = DOSSIER / "liste-des-gares.csv"
FICHIER_SORTIE = DOSSIER / "dvf_final_2020_2025_avec_enrichissements_gares.csv"


def titre(message):
    print("\n" + "=" * 100)
    print(message)
    print("=" * 100)


def sous_titre(message):
    print("\n" + "-" * 100)
    print(message)
    print("-" * 100)


def charger_gares_voyageurs():
    titre("1. CHARGEMENT ET PREPARATION DES GARES")

    print("On utilise uniquement les gares voyageurs, car ce sont les gares utiles pour les habitants.")
    print("Coordonnees utilisees :")
    print("- X_WGS84 = longitude")
    print("- Y_WGS84 = latitude")

    gares = pd.read_csv(FICHIER_GARES, sep=";", low_memory=False)

    print(f"Gares brutes : {gares.shape[0]:,} lignes x {gares.shape[1]} colonnes")
    print("\nApercu gares brutes :")
    print(gares[["LIBELLE", "COMMUNE", "VOYAGEURS", "X_WGS84", "Y_WGS84"]].head().to_string())

    gares["X_WGS84"] = pd.to_numeric(gares["X_WGS84"], errors="coerce")
    gares["Y_WGS84"] = pd.to_numeric(gares["Y_WGS84"], errors="coerce")

    gares_voyageurs = gares[
        (gares["VOYAGEURS"] == "O")
        & gares["X_WGS84"].between(-6, 10)
        & gares["Y_WGS84"].between(41, 52)
    ].copy()

    print(f"\nGares voyageurs avec GPS valide : {gares_voyageurs.shape[0]:,}")
    print("\nApercu gares retenues :")
    print(gares_voyageurs[["LIBELLE", "COMMUNE", "X_WGS84", "Y_WGS84"]].head(10).to_string())

    return gares_voyageurs


def creer_balltree_gares(gares_voyageurs):
    sous_titre("Creation de l'index spatial BallTree")

    print("BallTree permet de trouver rapidement la gare la plus proche.")
    print("La distance utilisee est haversine, adaptee aux coordonnees GPS.")

    # BallTree attend les coordonnees en radians, ordre latitude puis longitude.
    coords_gares = np.radians(
        gares_voyageurs[["Y_WGS84", "X_WGS84"]].values
    )

    tree = BallTree(coords_gares, metric="haversine")

    print("Index spatial cree.")
    return tree


def ajouter_distance_gares_par_chunks(tree):
    titre("2. AJOUT DE LA DISTANCE GARE AU FICHIER DVF ENRICHI")

    print("Le fichier DVF enrichi est volumineux, donc on le traite par morceaux.")
    print("Nouvelles colonnes creees :")
    print("- distance_gare_plus_proche_km")
    print("- gare_moins_5km")
    print("- gare_moins_10km")

    if not FICHIER_DVF_ENRICHI.exists():
        raise FileNotFoundError(f"Fichier introuvable : {FICHIER_DVF_ENRICHI}")

    if FICHIER_SORTIE.exists():
        print(f"\nLe fichier de sortie existe deja, il sera remplace : {FICHIER_SORTIE.name}")
        FICHIER_SORTIE.unlink()

    rayon_terre_km = 6371.0088
    chunksize = 250_000
    total_lignes = 0
    numero_chunk = 0
    debut = time.time()

    for chunk in pd.read_csv(
        FICHIER_DVF_ENRICHI,
        chunksize=chunksize,
        low_memory=False,
    ):
        numero_chunk += 1

        print("\n" + "-" * 80)
        print(f"Traitement chunk {numero_chunk}")
        print("-" * 80)
        print(f"Lignes dans ce chunk : {chunk.shape[0]:,}")

        # Securiser les coordonnees des biens.
        chunk["latitude"] = pd.to_numeric(chunk["latitude"], errors="coerce")
        chunk["longitude"] = pd.to_numeric(chunk["longitude"], errors="coerce")

        gps_ok = (
            chunk["latitude"].notna()
            & chunk["longitude"].notna()
            & chunk["latitude"].between(41, 52)
            & chunk["longitude"].between(-6, 10)
        )

        print(f"Biens avec GPS valide : {gps_ok.sum():,} / {len(chunk):,}")

        chunk["distance_gare_plus_proche_km"] = np.nan
        chunk["gare_moins_5km"] = 0
        chunk["gare_moins_10km"] = 0

        if gps_ok.any():
            coords_biens = np.radians(
                chunk.loc[gps_ok, ["latitude", "longitude"]].values
            )

            distances_rad, _ = tree.query(coords_biens, k=1)
            distances_km = distances_rad.flatten() * rayon_terre_km

            chunk.loc[gps_ok, "distance_gare_plus_proche_km"] = distances_km
            chunk.loc[gps_ok, "gare_moins_5km"] = (distances_km <= 5).astype(int)
            chunk.loc[gps_ok, "gare_moins_10km"] = (distances_km <= 10).astype(int)

            print("Statistiques distance sur ce chunk :")
            print(pd.Series(distances_km).describe().to_string())

        mode = "w" if numero_chunk == 1 else "a"
        header = numero_chunk == 1

        chunk.to_csv(
            FICHIER_SORTIE,
            mode=mode,
            header=header,
            index=False,
        )

        total_lignes += chunk.shape[0]
        print(f"Chunk {numero_chunk} sauvegarde.")
        print(f"Total lignes traitees : {total_lignes:,}")
        print(f"Temps ecoule : {(time.time() - debut) / 60:.2f} minutes")

    titre("AJOUT DES GARES TERMINE")
    print(f"Fichier cree : {FICHIER_SORTIE}")
    print(f"Nombre total de lignes : {total_lignes:,}")
    print(f"Temps total : {(time.time() - debut) / 60:.2f} minutes")


def main():
    debut = time.time()

    titre("DEBUT AJOUT DISTANCE AUX GARES")

    print("Fichiers utilises :")
    print(f"- DVF enrichi : {FICHIER_DVF_ENRICHI}")
    print(f"- Gares       : {FICHIER_GARES}")
    print(f"- Sortie      : {FICHIER_SORTIE}")

    if not FICHIER_GARES.exists():
        raise FileNotFoundError(f"Fichier gares introuvable : {FICHIER_GARES}")

    gares_voyageurs = charger_gares_voyageurs()
    tree = creer_balltree_gares(gares_voyageurs)
    ajouter_distance_gares_par_chunks(tree)

    titre("TRAITEMENT TERMINE")
    print(f"Temps global : {(time.time() - debut) / 60:.2f} minutes")


if __name__ == "__main__":
    main()
