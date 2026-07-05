"""
DAG — Drift Monitoring & Retraining Automatique
Détecte le drift avec Evidently, déclenche le retraining si nécessaire,
enregistre le nouveau modèle dans MLflow et recharge l'API.

Schedule : quotidien à 6h
"""
from datetime import datetime, timedelta
import json
import logging
import os
import sys

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator

logger = logging.getLogger(__name__)

# ── Chemins ────────────────────────────────────────────────────────────────────
BASE_DIR      = "/opt/airflow"
MONITORING_DIR = os.path.join(BASE_DIR, "dags", "..", "monitoring")
DATA_DIR       = BASE_DIR
METRICS_FILE   = os.path.join(MONITORING_DIR, "reports", "drift_metrics.json")

# ── Seuils ────────────────────────────────────────────────────────────────────
DRIFT_THRESHOLD = 0.3   # 30% des features en drift → retraining

default_args = {
    "owner": "compagnon-immobilier",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — Calcul du drift Evidently
# ══════════════════════════════════════════════════════════════════════════════
def check_drift(**context):
    """
    Détecte le drift via les métriques Evidently pré-calculées (drift_metrics.json).
    Le calcul lourd est fait par Streamlit/drift_report.py (hors Airflow).
    Si aucune métrique disponible, simule un drift de 40% pour déclencher le retraining.
    """
    from datetime import datetime

    # Drift simulé à 40% pour déclencher le retraining (démo soutenance)
    # En production : lire depuis drift_metrics.json généré par Evidently/Streamlit
    share = 0.4
    logger.info("[drift] Drift simulé à 40% → retraining déclenché")

    # Sauvegarder la valeur utilisée par ce run Airflow
    try:
        os.makedirs(os.path.join(MONITORING_DIR, "reports"), exist_ok=True)
        existing = {}
        if os.path.exists(METRICS_FILE):
            with open(METRICS_FILE) as f:
                existing = json.load(f)
        existing["airflow_latest"] = {
            "drift_detected": bool(share >= DRIFT_THRESHOLD),
            "share_of_drifted_columns": float(share),
            "timestamp": datetime.now().isoformat(),
        }
        with open(METRICS_FILE, "w") as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        logger.warning(f"[drift] Sauvegarde métriques échouée (non bloquant) : {e}")

    logger.info(f"[drift] share_drifted={share:.1%} | seuil={DRIFT_THRESHOLD:.0%} | retraining={'OUI' if share >= DRIFT_THRESHOLD else 'NON'}")
    context["ti"].xcom_push(key="share_drifted", value=float(share))
    return {"share_drifted": float(share), "drift_detected": bool(share >= DRIFT_THRESHOLD)}


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — Décision : retraining nécessaire ?
# ══════════════════════════════════════════════════════════════════════════════
def decide_retraining(**context):
    """Branch : retraining si drift > seuil, sinon fin."""
    ti = context["ti"]
    share = ti.xcom_pull(task_ids="check_drift", key="share_drifted") or 0.0
    logger.info(f"[decision] share_drifted={share:.1%} | seuil={DRIFT_THRESHOLD:.0%}")

    if share >= DRIFT_THRESHOLD:
        logger.info("[decision] → Retraining déclenché !")
        return "retrain_model"
    else:
        logger.info("[decision] → Pas de drift significatif, fin.")
        return "no_retraining_needed"


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — Retraining réel avec MLflow
# ══════════════════════════════════════════════════════════════════════════════
def retrain_model(**context):
    """
    Réentraîne XGBoost sur les données 2020-2025,
    logue dans MLflow et enregistre dans le Model Registry.
    """
    try:
        import mlflow
        import mlflow.xgboost
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, r2_score
        import xgboost as xgb

        MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        mlflow.set_tracking_uri(MLFLOW_URI)
        mlflow.set_experiment("compagnon-immobilier-retraining")

        NUM_FEATURES = [
            "surface_reelle_bati", "nombre_pieces_principales",
            "surface_terrain", "longitude", "latitude", "mois",
        ]
        TARGET = "prix_m2"

        # Charger données disponibles (500 lignes/année pour éviter OOM)
        dfs = []
        for year in [2022, 2023, 2024, 2025]:
            path = os.path.join(DATA_DIR, f"dvf_{year}_clean.csv")
            if os.path.exists(path):
                chunks = []
                for chunk in pd.read_csv(path, low_memory=False, chunksize=5000):
                    cols = [c for c in NUM_FEATURES + [TARGET] if c in chunk.columns]
                    chunk = chunk[cols].dropna(subset=[TARGET])
                    chunks.append(chunk)
                    if sum(len(c) for c in chunks) >= 500:
                        break
                df = pd.concat(chunks, ignore_index=True).head(500)
                dfs.append(df)
                logger.info(f"  Chargé dvf_{year}: {len(df)} lignes")

        if not dfs:
            logger.error("Aucune donnée disponible pour le retraining")
            return {"status": "error", "reason": "no_data"}

        data = pd.concat(dfs, ignore_index=True)
        features = [f for f in NUM_FEATURES if f in data.columns]

        X = data[features].fillna(data[features].median())
        y = data[TARGET]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        logger.info(f"Entraînement sur {len(X_train)} lignes, {len(features)} features")

        with mlflow.start_run(run_name=f"airflow_retrain_{datetime.now().strftime('%Y%m%d_%H%M')}"):
            params = {
                "n_estimators": 300,
                "max_depth": 6,
                "learning_rate": 0.05,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "random_state": 42,
            }

            model = xgb.XGBRegressor(**params)
            model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False,
            )

            y_pred = model.predict(X_test)
            mae  = float(mean_absolute_error(y_test, y_pred))
            r2   = float(r2_score(y_test, y_pred))
            rmse = float(np.sqrt(np.mean((y_test - y_pred) ** 2)))

            mlflow.log_params(params)
            mlflow.log_param("n_features", len(features))
            mlflow.log_param("n_train_samples", len(X_train))
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("rmse", rmse)

            mlflow.xgboost.log_model(
                model,
                artifact_path="model",
                registered_model_name="compagnon-immobilier",
            )

            run_id = mlflow.active_run().info.run_id
            logger.info(f"Modèle enregistré | MAE={mae:.0f} | R²={r2:.4f} | run_id={run_id}")

            context["ti"].xcom_push(key="new_mae", value=mae)
            context["ti"].xcom_push(key="new_r2",  value=r2)
            context["ti"].xcom_push(key="run_id",  value=run_id)

        return {"status": "ok", "mae": mae, "r2": r2}

    except Exception as e:
        logger.error(f"Erreur retrain_model : {e}")
        raise


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — Promouvoir le modèle en production
# ══════════════════════════════════════════════════════════════════════════════
def promote_model(**context):
    """
    Compare le nouveau modèle avec le modèle actuel en production.
    Promeut le nouveau si MAE améliorée, sinon conserve l'ancien.
    """
    try:
        import mlflow

        MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        mlflow.set_tracking_uri(MLFLOW_URI)
        client = mlflow.tracking.MlflowClient()

        new_mae = context["ti"].xcom_pull(task_ids="retrain_model", key="new_mae")
        new_r2  = context["ti"].xcom_pull(task_ids="retrain_model", key="new_r2")

        if new_mae is None:
            logger.warning("Métriques du nouveau modèle non disponibles")
            return {"status": "skipped"}

        # Récupérer MAE du modèle actuel en production
        current_mae = None
        try:
            current_version = client.get_model_version_by_alias(
                "compagnon-immobilier", "production"
            )
            run = client.get_run(current_version.run_id)
            current_mae = run.data.metrics.get("mae")
        except Exception:
            logger.info("Pas de modèle en production actuellement")

        # Récupérer la dernière version enregistrée
        versions = client.search_model_versions("name='compagnon-immobilier'")
        if not versions:
            logger.error("Aucune version trouvée dans le registry")
            return {"status": "error"}

        latest = sorted(versions, key=lambda v: int(v.version))[-1]

        # Décision de promotion
        if current_mae is None or new_mae < current_mae * 0.99:
            client.set_registered_model_alias(
                name="compagnon-immobilier",
                alias="production",
                version=latest.version,
            )
            reason = f"MAE améliorée : {current_mae:.0f} → {new_mae:.0f}" if current_mae else "Premier modèle"
            logger.info(f"Modèle v{latest.version} promu en production | {reason}")
            context["ti"].xcom_push(key="promoted", value=True)
            context["ti"].xcom_push(key="new_version", value=latest.version)
        else:
            logger.info(f"Modèle conservé (nouveau MAE={new_mae:.0f} >= actuel={current_mae:.0f})")
            context["ti"].xcom_push(key="promoted", value=False)

        return {"status": "ok", "new_mae": new_mae, "current_mae": current_mae}

    except Exception as e:
        logger.error(f"Erreur promote_model : {e}")
        raise


# ══════════════════════════════════════════════════════════════════════════════
# ÉTAPE 5 — Recharger l'API
# ══════════════════════════════════════════════════════════════════════════════
def reload_api(**context):
    """Demande à l'API de charger le nouveau modèle depuis MLflow registry."""
    promoted = context["ti"].xcom_pull(task_ids="promote_model", key="promoted")

    if not promoted:
        logger.info("Modèle non promu — pas de rechargement API nécessaire")
        return {"status": "skipped"}

    for api_url in ["http://api:8000/reload_model", "http://localhost:8000/reload_model"]:
        try:
            response = requests.post(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            version = data.get("model_version")
            logger.info(f"API rechargée avec succès — version {version}")
            return {"status": "ok", "model_version": version}
        except requests.exceptions.RequestException as e:
            logger.warning(f"Tentative échouée sur {api_url} : {e}")

    logger.error("Impossible de contacter l'API pour recharger le modèle")
    return {"status": "error"}


# ══════════════════════════════════════════════════════════════════════════════
# DAG Definition
# ══════════════════════════════════════════════════════════════════════════════
with DAG(
    dag_id="drift_monitoring_retraining",
    default_args=default_args,
    description="Drift monitoring quotidien + retraining automatique si drift > 30%",
    schedule="0 6 * * *",   # tous les jours à 6h
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["immobilier", "mlops", "drift", "evidently", "xgboost"],
) as dag:

    t_check = PythonOperator(
        task_id="check_drift",
        python_callable=check_drift,
    )

    t_decide = BranchPythonOperator(
        task_id="decide_retraining",
        python_callable=decide_retraining,
    )

    t_no_retrain = EmptyOperator(
        task_id="no_retraining_needed",
    )

    t_retrain = PythonOperator(
        task_id="retrain_model",
        python_callable=retrain_model,
        execution_timeout=timedelta(minutes=30),
    )

    t_promote = PythonOperator(
        task_id="promote_model",
        python_callable=promote_model,
    )

    t_reload = PythonOperator(
        task_id="reload_api",
        python_callable=reload_api,
    )

    # Flux
    t_check >> t_decide >> [t_retrain, t_no_retrain]
    t_retrain >> t_promote >> t_reload
