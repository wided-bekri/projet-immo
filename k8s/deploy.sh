#!/bin/bash
# Script de déploiement complet — Compagnon Immobilier sur Kubernetes
# Usage : bash k8s/deploy.sh

set -e

echo "🚀 Déploiement Compagnon Immobilier sur Kubernetes"
echo "=================================================="

# 1. Namespace
echo "📁 Création du namespace immo..."
kubectl apply -f k8s/namespace.yml

# 2. Secrets & ConfigMaps
echo "🔐 Application des Secrets..."
kubectl apply -f k8s/secrets/secrets.yml
echo "⚙️  Application des ConfigMaps..."
kubectl apply -f k8s/configmaps/configmaps.yml

# 3. Stockage persistant
echo "💾 Création des volumes persistants..."
kubectl apply -f k8s/storage/persistent-volumes.yml

# 4. Déploiements (ordre important : postgres avant airflow)
echo "🗄️  Déploiement PostgreSQL..."
kubectl apply -f k8s/deployments/postgres.yml
echo "⏳ Attente PostgreSQL (30s)..."
sleep 30

echo "📦 Déploiement MLflow..."
kubectl apply -f k8s/deployments/mlflow.yml

echo "🤖 Déploiement API FastAPI..."
kubectl apply -f k8s/deployments/api.yml

echo "⛓️  Déploiement Airflow..."
kubectl apply -f k8s/deployments/airflow.yml

echo "📊 Déploiement Prometheus & Grafana..."
kubectl apply -f k8s/deployments/monitoring.yml

echo "🎨 Déploiement Streamlit..."
kubectl apply -f k8s/deployments/streamlit.yml

# 5. Services
echo "🔌 Application des Services..."
kubectl apply -f k8s/services/services.yml

echo ""
echo "✅ Déploiement terminé !"
echo ""
echo "📍 Accès aux services :"
echo "   Streamlit  : http://IP_VM:30501"
echo "   Airflow    : http://IP_VM:30080"
echo "   Prometheus : http://IP_VM:30090"
echo "   Grafana    : http://IP_VM:30030"
echo ""
echo "🔍 Vérification : kubectl get all -n immo"
