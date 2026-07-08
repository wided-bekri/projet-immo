import streamlit as st

st.set_page_config(page_title="Architecture MLOps", layout="wide")

# CSS pour un effet Wahou (Blocs volumineux et animations)
st.markdown("""
<style>
    .big-block {
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 5px;
        font-weight: bold;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s;
        font-size: 0.9rem;
    }
    .big-block:hover { transform: scale(1.05); }
    .gouv { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    .pipeline { background: linear-gradient(135deg, #7b1fa2 0%, #9c27b0 100%); }
    .serve { background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%); }
    .monit { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .cicd { background: linear-gradient(135deg, #e91e63 0%, #d81b60 100%); }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Architecture MLOps : Système Compagnon Immobilier")
st.markdown("---")

# Visualisation des Flux en 4 colonnes
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="big-block gouv">📂 DATA & GOUVERNANCE<br><br>DVF 4.48M → DVC → Airflow → XGBoost → MLflow</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="big-block serve">🐳 DEPLOYMENT<br><br>Docker Compose → Nginx → FastAPI → Streamlit</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="big-block monit">📡 MONITORING<br><br>Prometheus → Grafana → Evidently → Retrain</div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="big-block cicd">🔐 CI/CD<br><br>GitHub Actions<br>Tests + Lint (Ruff)</div>', unsafe_allow_html=True)

st.markdown("---")

# Diagramme Interactif Mermaid Grand Format
mermaid_code = """
<div class="mermaid" style="width:100%; height:550px;">
graph TD
    subgraph Gouv [📂 1. DATA & GOUVERNANCE]
        DVF((DVF 4.48M)) --> DVC[DVC + DagsHub]
        DVC --> Airflow[AIRFLOW DAGs]
        Airflow --> XGB[🤖 XGBOOST]
        XGB --> MLR[📊 MLFLOW]
    end
    subgraph Deploy [🐳 2. DEPLOYMENT]
        MLR --> DOCK[DOCKER COMPOSE]
        DOCK --> NGINX[NGINX]
        NGINX --> API[⚡ FASTAPI]
        API --> ST[🏠 STREAMLIT]
    end
    subgraph Monitor [📡 3. MONITORING]
        API --> PROM[PROMETHEUS]
        PROM --> GRAF[GRAFANA]
        API --> EVI[🔍 EVIDENTLY DRIFT]
        EVI --"Drift > 30%"--> RETRAIN[🔄 RETRAINING AUTO]
        RETRAIN --> Airflow
    end
    subgraph CI [🔐 4. CI/CD]
        GIT[GitHub Actions] --> TEST[Tests Unitaires]
        TEST --> LINT[Ruff Linting]
    end
    style Gouv fill:#e3f2fd,stroke:#1e3c72
    style Deploy fill:#fff8e1,stroke:#f2994a
    style Monitor fill:#e8f5e9,stroke:#11998e
    style CI fill:#fce4ec,stroke:#e91e63
</div>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad:true, theme: 'forest'});</script>
"""
st.components.v1.html(mermaid_code, height=550, scrolling=True)

# Détails en dessous
st.markdown("---")
cols = st.columns(3)
cols[0].markdown("### 📊 Chiffres Clés\n- 4,48M transactions\n- 31 features\n- MAE 648€/m² (R² 0.80)\n- 10 microservices")
cols[1].markdown("### 🛠️ Stack Technique\n- Versioning: DVC + DagsHub\n- Orchestration: Airflow 2.9\n- Tracking: MLflow 3.14\n- Serving: FastAPI + Nginx")
cols[2].markdown("### 🔄 Pipeline Auto\n- Détection Drift (Quotidien)\n- Retraining auto (>30%)\n- Registry MLflow\n- Zero-downtime Reload")

st.markdown("---")
st.markdown("---")
st.subheader("💡 Retour d'Expérience & Enseignements MLOps")

# Utilisation d'un expander pour garder une page aérée
with st.expander("🛠️ Défis rencontrés & Retour d'expérience", expanded=True):
    col_defis, col_enseignements = st.columns([1, 1])
    
    with col_defis:
        st.markdown("""
        **📦 Reproductibilité**
        * Absence d'artefacts ML après clonage du projet.
        * Configuration DVC/DagsHub indispensable pour restaurer modèles et datasets.
        
        **🐳 Docker & Orchestration**
        * Erreurs de build (fichiers manquants, chemins incorrects).
        * Healthchecks mal configurés bloquant le démarrage des services.
        
        **🔗 Intégration des services**
        * Harmonisation du flux Streamlit → API → Prometheus.
        * Synchronisation Airflow → MLflow pour une traçabilité réelle.
        """)
        
    with col_enseignements:
        st.markdown("""
        **✅ Ce que nous avons appris :**
        * Un modèle qui fonctionne "en local" n’est pas nécessairement prêt pour la production.
        * La reproductibilité absolue repose sur la maîtrise tripartite : **Données + Code + Environnement.**
        * Le rôle du MLOps n'est pas seulement technique : c'est transformer un prototype isolé en un **service fiable, maintenable et évolutif.**
        """)

# Un petit message final pour clore la page avec élégance
st.success("🎯 **Conclusion :** Nous sommes passés d'un modèle prédictif isolé à une véritable architecture industrielle capable d'être reproduite et maintenue dans le temps.")