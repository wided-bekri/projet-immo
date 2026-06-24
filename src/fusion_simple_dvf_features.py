from pathlib import Path
import time

import pandas as pd


# ============================================================
# FUSION SIMPLE : DVF FINAL + FEATURES COMMUNALES
# ============================================================
#
# Objectif :
# - Charger dvf_final_2020_2025.csv
# - Charger features_communes_clean.csv
# - Fusionner avec la colonne code_commune
# - Creer dvf_final_2020_2025_avec_enrichissements.csv
#
# Ce fichier ne fait PAS :
# - de nettoyage ML avance
# - de split train/test
# - de modelisation
# - de commune_prix_m2
# - de distance aux gares
# ============================================================


DOSSIER = Path(r"C:\Users\a\Desktop\Projet Immo")

FICHIER_DVF = DOSSIER / "dvf_final_2020_2025.csv"
FICHIER_FEATURES = DOSSIER / "features_communes_clean.csv"
FICHIER_SORTIE = DOSSIER / "dvf_final_2020_2025_avec_enrichissements.csv"


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
    Transforme les codes communes en texte sur 5 caracteres.

    Exemple :
    1001  -> 01001
    75056 -> 75056
    """
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)


def main():
    debut = time.time()

    titre("FUSION SIMPLE DVF + FEATURES COMMUNALES")

    print("Fichiers utilises :")
    print(f"- DVF      : {FICHIER_DVF}")
    print(f"- Features : {FICHIER_FEATURES}")
    print(f"- Sortie   : {FICHIER_SORTIE}")

    if not FICHIER_DVF.exists():
        raise FileNotFoundError(f"Fichier DVF introuvable : {FICHIER_DVF}")

    if not FICHIER_FEATURES.exists():
        raise FileNotFoundError(f"Fichier features introuvable : {FICHIER_FEATURES}")

    # --------------------------------------------------------
    # 1. Charger les features communales
    # --------------------------------------------------------
    sous_titre("1. Chargement de features_communes_clean.csv")

    features = pd.read_csv(
        FICHIER_FEATURES,
        dtype={"code_commune": str},
        low_memory=False,
    )

    features["code_commune"] = code_commune_5(features["code_commune"])

    print(f"Features chargees : {features.shape[0]:,} lignes x {features.shape[1]} colonnes")
    print("\nApercu features :")
    print(features.head().to_string())

    # --------------------------------------------------------
    # 2. Lire DVF par morceaux et fusionner
    # --------------------------------------------------------
    sous_titre("2. Fusion par morceaux avec dvf_final_2020_2025.csv")

    print("Le fichier DVF est volumineux, donc on le lit par morceaux.")
    print("Cela evite de saturer la memoire de l'ordinateur.")

    if FICHIER_SORTIE.exists():
        print(f"\nLe fichier de sortie existe deja, il sera remplace : {FICHIER_SORTIE.name}")
        FICHIER_SORTIE.unlink()

    chunksize = 250_000
    total_lignes = 0
    numero_chunk = 0

    for chunk in pd.read_csv(
        FICHIER_DVF,
        chunksize=chunksize,
        dtype={"code_commune": str},
        low_memory=False,
    ):
        numero_chunk += 1

        print("\n" + "-" * 80)
        print(f"Traitement chunk {numero_chunk}")
        print("-" * 80)
        print(f"Lignes dans ce chunk : {chunk.shape[0]:,}")

        # Harmoniser le code commune avant fusion.
        chunk["code_commune"] = code_commune_5(chunk["code_commune"])

        # Fusion gauche : on conserve toutes les lignes DVF.
        chunk_fusion = chunk.merge(
            features,
            on="code_commune",
            how="left",
        )

        print(f"Colonnes avant fusion : {chunk.shape[1]}")
        print(f"Colonnes apres fusion : {chunk_fusion.shape[1]}")

        if "population_2023" in chunk_fusion.columns:
            taux_sans_population = chunk_fusion["population_2023"].isna().mean() * 100
            print(f"Lignes sans correspondance population_2023 : {taux_sans_population:.2f} %")

        # Sauvegarde progressive dans le fichier final.
        mode = "w" if numero_chunk == 1 else "a"
        header = numero_chunk == 1

        chunk_fusion.to_csv(
            FICHIER_SORTIE,
            mode=mode,
            header=header,
            index=False,
        )

        total_lignes += chunk_fusion.shape[0]
        print(f"Chunk {numero_chunk} sauvegarde.")
        print(f"Total lignes traitees : {total_lignes:,}")
        print(f"Temps ecoule : {(time.time() - debut) / 60:.2f} minutes")

    # --------------------------------------------------------
    # 3. Fin
    # --------------------------------------------------------
    titre("FUSION TERMINEE")
    print(f"Fichier cree : {FICHIER_SORTIE}")
    print(f"Nombre total de lignes : {total_lignes:,}")
    print(f"Temps total : {(time.time() - debut) / 60:.2f} minutes")


if __name__ == "__main__":
    main()
