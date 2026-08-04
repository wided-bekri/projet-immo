import streamlit as st
import time

st.set_page_config(page_title="Architecture MLOps", layout="wide")

# --- CSS PREMIUM ---
st.markdown("""
<style>
    .pillar-card { padding: 20px; border-radius: 15px; text-align: center; color: white; transition: 0.3s; }
    .pillar-card:hover { transform: scale(1.05); }
    .timeline-item { border-left: 3px solid #6c757d; padding-left: 20px; margin-bottom: 15px; position: relative; }
    .timeline-dot { width: 12px; height: 12px; background: #6c757d; border-radius: 50%; position: absolute; left: -8px; top: 5px; }
</style>
""", unsafe_allow_html=True)

# 1. Header Premium
st.title("🏗️ Architecture MLOps : Industrialiser le cycle de vie d’un modèle")
st.info("De la donnée versionnée au service intelligent supervisé")

# 2. Parcours Utilisateur + Flux de Production (Côte à côte)
col_top1, col_top2 = st.columns([1, 1])

with col_top1:
    st.subheader("🔄 Parcours utilisateur")
    st.markdown("""
    ```mermaid
    graph TD
    A[Utilisateur] --> B[Streamlit]
    B --> C[Nginx]
    C --> D[FastAPI]
    D --> E[MLflow Registry]
    E --> F[XGBoost]
    F --> G[Résultat]
    D -.-> H[Prometheus]
    H --> I[Grafana]
    ```
    """)

with col_top2:
    st.subheader("⚡ Flux de production")
    placeholder = st.empty()
    for text in ["👤 Utilisateur", "📱 Streamlit", "⚡ API FastAPI", "🤖 Modèle XGBoost", "🏠 Estimation !"]:
        placeholder.markdown(f"### ➡️ {text}")
        time.sleep(.3)

st.markdown("---")

# 3. Les 4 Piliers
st.subheader("Les 4 Piliers de l'Architecture")
cols = st.columns(4)
piliers = [
    ("📂 Gouvernance", "#1e3c72", "DVC • DagsHub • MLflow"),
    ("⚙️ Automatisation", "#7b1fa2", "Pipelines Airflow"),
    ("🚀 Déploiement", "#f2994a", "Docker • FastAPI • Nginx"),
    ("📈 Monitoring", "#11998e", "Prometheus • Grafana • Evidently")
]

for i, (titre, color, desc) in enumerate(piliers):
    with cols[i]:
        st.markdown(f'<div class="pillar-card" style="background-color: {color};"><h3>{titre}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

st.markdown("---")

# 4. Cycle de vie complet (Largeur totale)
st.subheader("🔁 Cycle de vie & Évolution complète")
st.markdown("""
    ```mermaid
    graph LR
        subgraph CI [🔐 Couche Transversale CI : Qualité & Tests]
            Actions[GitHub Actions] --> Test[Tests & Linting]
        end

        A[Data: DVF/INSEE] --> B[Pipeline Airflow]
        B --> C[Entraînement]
        C --> D[MLflow Registry]
        D --> E[FastAPI/Streamlit]
        E -.-> F[Evidently Drift]
        F --"Drift > 30%"--> B
        
        CI -.-> B
        CI -.-> C
        CI -.-> E
        
        style CI fill:#fce4ec,stroke:#e91e63,stroke-dasharray: 5 5
    ```
    """)

st.markdown("---")

# 5. KPI Professionnels
st.subheader("Modèle & Infrastructure en chiffres")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Transactions", "4,48 M")
kpi2.metric("Features", "31")
kpi3.metric("R² Score", "0.80")
kpi4.metric("MAE", "648 €/m²")
kpi5.metric("Conteneurs Docker", "10")

st.markdown("---")

# 6. REX : Chemin vers la production
st.subheader("🛠️ Retour d'expérience : Le chemin vers la production")
col1, col2 = st.columns([1, 1])

with col1:
    steps = [
        ("Git Clone", "Code récupéré"),
        ("DVC Pull", "Données & Artefacts restaurés"),
        ("Docker Build", "Conteneurs isolés"),
        ("Healthchecks", "Services synchronisés"),
        ("Pipeline OK", "Entraînement automatisé"),
        ("Application OK", "Service opérationnel")
    ]
    for step, desc in steps:
        st.markdown(f'<div class="timeline-item"><div class="timeline-dot"></div><strong>{step}</strong><br><small>{desc}</small></div>', unsafe_allow_html=True)

with col2:
    st.info("### 🎓 Ce que nous avons appris")
    st.markdown("""
    * **La rigueur est la clé :** Un modèle performant en local n'est rien sans un déploiement robuste.
    * **Reproductibilité absolue :** DVC et DagsHub sont nos seuls garants contre l'obsolescence.
    * **Industrialisation :** Automatiser les tests (CI) permet de garantir la fiabilité lors des mises à jour.
    * **Culture MLOps :** Le monitoring n'est pas optionnel, c'est ce qui transforme le code en un **produit**.
    """)

# 7. Conclusion
st.success("""
### 🎯 À retenir
Notre objectif n'était pas seulement de construire un modèle performant, 
mais une architecture capable de le faire vivre dans le temps.
Le MLOps transforme un prototype Data Science en un véritable service industriel.
""")

st.warning("Détaillons maintenant les composants techniques et l'infrastructure sous-jacente.")