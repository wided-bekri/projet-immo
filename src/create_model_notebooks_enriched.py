import json
from pathlib import Path


BASE_DIR = Path(r"C:\Users\a\Desktop\Projet Immo")
OUT_DIR = BASE_DIR / "notebooks" / "Models_enriched"
OUT_DIR.mkdir(parents=True, exist_ok=True)


COMMON_HELPERS = r'''
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

pd.set_option("display.max_columns", None)

DATA_DIR = r"C:\Users\a\Desktop\Projet Immo"

X_TRAIN_PATH = f"{DATA_DIR}\\X_train_enriched.csv"
X_TEST_PATH = f"{DATA_DIR}\\X_test_enriched.csv"
Y_TRAIN_PATH = f"{DATA_DIR}\\y_train_enriched.csv"
Y_TEST_PATH = f"{DATA_DIR}\\y_test_enriched.csv"


def charger_donnees():
    print("=" * 80)
    print("CHARGEMENT DES DONNEES ENRICHIES")
    print("=" * 80)
    start = time.time()

    X_train = pd.read_csv(X_TRAIN_PATH, low_memory=False)
    X_test = pd.read_csv(X_TEST_PATH, low_memory=False)
    y_train = pd.read_csv(Y_TRAIN_PATH, low_memory=False).values.ravel()
    y_test = pd.read_csv(Y_TEST_PATH, low_memory=False).values.ravel()

    print(f"Chargement termine en {(time.time() - start) / 60:.2f} minutes")
    print(f"X_train : {X_train.shape}")
    print(f"X_test  : {X_test.shape}")
    print(f"y_train : {y_train.shape}")
    print(f"y_test  : {y_test.shape}")

    print("\nApercu des variables :")
    display(X_train.head())

    print("\nValeurs manquantes X_train :")
    print(X_train.isna().sum().sum())

    return X_train, X_test, y_train, y_test


def calculer_metriques(y_test, y_pred):
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100
    return r2, mae, rmse, mape


def afficher_resultats(nom_modele, y_test, y_pred, train_time, pred_time):
    r2, mae, rmse, mape = calculer_metriques(y_test, y_pred)

    print("\n" + "=" * 80)
    print(f"RESULTATS : {nom_modele}")
    print("=" * 80)
    print(f"R2   : {r2:.4f}")
    print(f"MAE  : {mae:,.2f} euros")
    print(f"RMSE : {rmse:,.2f} euros")
    print(f"MAPE : {mape:.2f} %")
    print(f"Temps entrainement : {train_time / 60:.2f} minutes")
    print(f"Temps prediction   : {pred_time:.2f} secondes")

    return {
        "modele": nom_modele,
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "train_time_sec": train_time,
        "pred_time_sec": pred_time,
    }


def graphique_predictions(nom_modele, y_test, y_pred, n=5000):
    n = min(n, len(y_test))
    idx = np.random.RandomState(42).choice(len(y_test), size=n, replace=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test[idx], y_pred[idx], alpha=0.25)
    limite = max(y_test[idx].max(), y_pred[idx].max())
    plt.plot([0, limite], [0, limite], color="red")
    plt.xlabel("Prix reel")
    plt.ylabel("Prix predit")
    plt.title(f"{nom_modele} : prix reels vs prix predits")
    plt.grid(True)
    plt.show()
'''


def notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.splitlines(True)}


MODELS = {
    "01_linear_regression_enriched.ipynb": {
        "title": "Linear Regression enrichie",
        "code": r'''
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

NOM_MODELE = "Linear Regression enrichie"

X_train, X_test, y_train, y_test = charger_donnees()

model = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LinearRegression())
])

print("\nModele cree :")
print(model)

start = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start

start = time.time()
y_pred = model.predict(X_test)
pred_time = time.time() - start

resultat = afficher_resultats(NOM_MODELE, y_test, y_pred, train_time, pred_time)
graphique_predictions(NOM_MODELE, y_test, y_pred)

pd.DataFrame([resultat]).to_csv(f"{DATA_DIR}\\result_linear_regression_enriched.csv", index=False)
print("\nResultat sauvegarde : result_linear_regression_enriched.csv")
''',
        "interpretation": "Linear Regression sert de baseline simple. Si son score reste faible, cela confirme que le prix immobilier ne suit pas une relation uniquement lineaire.",
    },
    "02_ridge_regression_enriched.ipynb": {
        "title": "Ridge Regression enrichie",
        "code": r'''
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

NOM_MODELE = "Ridge Regression enrichie"

X_train, X_test, y_train, y_test = charger_donnees()

model = Pipeline([
    ("scaler", StandardScaler()),
    ("model", Ridge(alpha=1.0))
])

print("\nModele cree :")
print(model)

start = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start

start = time.time()
y_pred = model.predict(X_test)
pred_time = time.time() - start

resultat = afficher_resultats(NOM_MODELE, y_test, y_pred, train_time, pred_time)
graphique_predictions(NOM_MODELE, y_test, y_pred)

coefs = model.named_steps["model"].coef_
importance_df = pd.DataFrame({
    "variable": X_train.columns,
    "coefficient": coefs,
    "coefficient_abs": np.abs(coefs)
}).sort_values("coefficient_abs", ascending=False)

print("\nTop variables Ridge :")
display(importance_df.head(15))

pd.DataFrame([resultat]).to_csv(f"{DATA_DIR}\\result_ridge_regression_enriched.csv", index=False)
importance_df.to_csv(f"{DATA_DIR}\\importance_ridge_regression_enriched.csv", index=False)
print("\nResultats sauvegardes.")
''',
        "interpretation": "Ridge est une regression lineaire regularisee. Elle reduit les coefficients extremes, mais reste limitee si les relations sont non lineaires.",
    },
    "03_random_forest_enriched.ipynb": {
        "title": "Random Forest enrichi",
        "code": r'''
from sklearn.ensemble import RandomForestRegressor

NOM_MODELE = "Random Forest enrichi"

X_train, X_test, y_train, y_test = charger_donnees()

model = RandomForestRegressor(
    n_estimators=100,
    max_depth=18,
    min_samples_leaf=20,
    max_samples=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

print("\nModele cree :")
print(model)

start = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start

start = time.time()
y_pred = model.predict(X_test)
pred_time = time.time() - start

resultat = afficher_resultats(NOM_MODELE, y_test, y_pred, train_time, pred_time)
graphique_predictions(NOM_MODELE, y_test, y_pred)

importance_df = pd.DataFrame({
    "variable": X_train.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\nTop variables Random Forest :")
display(importance_df.head(15))

plt.figure(figsize=(10, 6))
sns.barplot(data=importance_df.head(15), x="importance", y="variable", hue="variable", legend=False)
plt.title("Top 15 variables - Random Forest enrichi")
plt.show()

pd.DataFrame([resultat]).to_csv(f"{DATA_DIR}\\result_random_forest_enriched.csv", index=False)
importance_df.to_csv(f"{DATA_DIR}\\importance_random_forest_enriched.csv", index=False)
print("\nResultats sauvegardes.")
''',
        "interpretation": "Random Forest capte les relations non lineaires. Les parametres limitent le surapprentissage.",
    },
    "04_extratrees_enriched.ipynb": {
        "title": "ExtraTrees enrichi",
        "code": r'''
from sklearn.ensemble import ExtraTreesRegressor

NOM_MODELE = "ExtraTrees enrichi"

X_train, X_test, y_train, y_test = charger_donnees()

model = ExtraTreesRegressor(
    n_estimators=100,
    max_depth=20,
    min_samples_leaf=10,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

print("\nModele cree :")
print(model)

start = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start

start = time.time()
y_pred = model.predict(X_test)
pred_time = time.time() - start

resultat = afficher_resultats(NOM_MODELE, y_test, y_pred, train_time, pred_time)
graphique_predictions(NOM_MODELE, y_test, y_pred)

importance_df = pd.DataFrame({
    "variable": X_train.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\nTop variables ExtraTrees :")
display(importance_df.head(15))

plt.figure(figsize=(10, 6))
sns.barplot(data=importance_df.head(15), x="importance", y="variable", hue="variable", legend=False)
plt.title("Top 15 variables - ExtraTrees enrichi")
plt.show()

pd.DataFrame([resultat]).to_csv(f"{DATA_DIR}\\result_extratrees_enriched.csv", index=False)
importance_df.to_csv(f"{DATA_DIR}\\importance_extratrees_enriched.csv", index=False)
print("\nResultats sauvegardes.")
''',
        "interpretation": "ExtraTrees ressemble a Random Forest mais ajoute plus d'aleatoire. Il est souvent performant sur des donnees tabulaires.",
    },
    "05_lightgbm_enriched.ipynb": {
        "title": "LightGBM enrichi",
        "code": r'''
try:
    import lightgbm as lgb
except ImportError as exc:
    raise ImportError("LightGBM n'est pas installe. Installer avec : pip install lightgbm") from exc

NOM_MODELE = "LightGBM enrichi"

X_train, X_test, y_train, y_test = charger_donnees()

model = lgb.LGBMRegressor(
    objective="regression",
    n_estimators=800,
    learning_rate=0.05,
    num_leaves=64,
    max_depth=-1,
    min_child_samples=30,
    subsample=0.9,
    colsample_bytree=0.9,
    random_state=42,
    n_jobs=-1
)

print("\nModele cree :")
print(model)

start = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start

start = time.time()
y_pred = model.predict(X_test)
pred_time = time.time() - start

resultat = afficher_resultats(NOM_MODELE, y_test, y_pred, train_time, pred_time)
graphique_predictions(NOM_MODELE, y_test, y_pred)

importance_df = pd.DataFrame({
    "variable": X_train.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\nTop variables LightGBM :")
display(importance_df.head(15))

plt.figure(figsize=(10, 6))
sns.barplot(data=importance_df.head(15), x="importance", y="variable", hue="variable", legend=False)
plt.title("Top 15 variables - LightGBM enrichi")
plt.show()

pd.DataFrame([resultat]).to_csv(f"{DATA_DIR}\\result_lightgbm_enriched.csv", index=False)
importance_df.to_csv(f"{DATA_DIR}\\importance_lightgbm_enriched.csv", index=False)
print("\nResultats sauvegardes.")
''',
        "interpretation": "LightGBM est souvent le meilleur compromis vitesse/performance sur gros jeux tabulaires.",
    },
    "06_xgboost_enriched.ipynb": {
        "title": "XGBoost enrichi",
        "code": r'''
try:
    import xgboost as xgb
except ImportError as exc:
    raise ImportError("XGBoost n'est pas installe. Installer avec : pip install xgboost") from exc

NOM_MODELE = "XGBoost enrichi"

X_train, X_test, y_train, y_test = charger_donnees()

model = xgb.XGBRegressor(
    objective="reg:squarederror",
    n_estimators=800,
    learning_rate=0.05,
    max_depth=8,
    min_child_weight=10,
    subsample=0.9,
    colsample_bytree=0.9,
    tree_method="hist",
    random_state=42,
    n_jobs=-1
)

print("\nModele cree :")
print(model)

start = time.time()
model.fit(X_train, y_train)
train_time = time.time() - start

start = time.time()
y_pred = model.predict(X_test)
pred_time = time.time() - start

resultat = afficher_resultats(NOM_MODELE, y_test, y_pred, train_time, pred_time)
graphique_predictions(NOM_MODELE, y_test, y_pred)

importance_df = pd.DataFrame({
    "variable": X_train.columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

print("\nTop variables XGBoost :")
display(importance_df.head(15))

plt.figure(figsize=(10, 6))
sns.barplot(data=importance_df.head(15), x="importance", y="variable", hue="variable", legend=False)
plt.title("Top 15 variables - XGBoost enrichi")
plt.show()

pd.DataFrame([resultat]).to_csv(f"{DATA_DIR}\\result_xgboost_enriched.csv", index=False)
importance_df.to_csv(f"{DATA_DIR}\\importance_xgboost_enriched.csv", index=False)
print("\nResultats sauvegardes.")
''',
        "interpretation": "XGBoost est un modele de boosting puissant. Il peut mieux exploiter les nouvelles variables territoriales.",
    },
}


for filename, spec in MODELS.items():
    cells = [
        md(f"# {spec['title']}\n\nCe notebook utilise les fichiers enrichis : `X_train_enriched.csv`, `X_test_enriched.csv`, `y_train_enriched.csv`, `y_test_enriched.csv`."),
        code(COMMON_HELPERS),
        code(spec["code"]),
        md(f"## Interpretation\n\n{spec['interpretation']}\n\nA comparer ensuite avec les resultats avant enrichissement."),
    ]
    path = OUT_DIR / filename
    path.write_text(json.dumps(notebook(cells), ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
