import streamlit as st
import os

# 1. Configuration et chargement du thème graphique commun
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE, "assets", "style.css")

with open(CSS_FILE, encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# --- INJECTION DE STYLES SUPPLÉMENTAIRES POUR LES EFFETS AVANCÉS ---
st.markdown("""
<style>
    /* Effet de survol sur les cartes (containers) */
    div[data-testid="stVerticalBlockBorderWithLabel"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stVerticalBlockBorderWithLabel"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
    }
    /* Style pour la timeline */
    .timeline-step {
        text-align: center;
        padding: 15px;
        background-color: rgba(250, 250, 250, 0.05);
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 1. HERO SECTION (Haut de page) - MODIFIÉE (Plus claire, texte 100% blanc)
# ==========================================
hero_html = """
<div style="
    background: linear-gradient(rgba(17, 24, 39, 0.55), rgba(17, 24, 39, 0.65)), 
                url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80');
    background-size: cover;
    background-position: center;
    padding: 60px 30px;
    border-radius: 12px;
    text-align: center;
    color: #FFFFFF;
    margin-bottom: 40px;
    box-shadow: inset 0 0 100px rgba(0,0,0,0.2);
">
    <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 10px; color: #FFFFFF;">🏡 Compagnon Immobilier</h1>
    <h3 style="font-size: 1.5rem; font-weight: 400; margin-bottom: 25px; color: #FFFFFF; opacity: 1;">
        Plateforme d'intelligence territoriale et d'estimation immobilière
    </h3>
    <hr style="border-color: rgba(255,255,255,0.4); width: 50%; margin: 0 auto 25px auto;">
    <p style="font-size: 1.3rem; font-style: italic; letter-spacing: 1px; color: #FFFFFF; font-weight: 600; text-shadow: 1px 1px 4px rgba(0,0,0,0.6);">
        Comprendre un territoire. Estimer un bien. Éclairer une décision.
    </p>
</div>
"""
st.markdown(hero_html, unsafe_allow_html=True)


# ==========================================
# 2. LE PROBLÈME MÉTIER
# ==========================================
st.markdown("## 🎯 Le problème métier")

with st.container(border=True):
    st.markdown("<h3 style='text-align: center; margin-bottom: 25px;'>Pourquoi deux biens identiques n'ont-ils pas la même valeur ?</h3>", unsafe_allow_html=True)
    
    col_bienA, col_vs, col_bienB = st.columns([4, 2, 4])
    
    with col_bienA:
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.02); padding: 20px; border-radius: 8px; border-left: 5px solid #EF4444; text-align: center;">
            <span style="font-size: 3rem;">🏠</span>
            <h4>Bien A</h4>
            <p>📐 <b>100 m²</b><br>🚪 <b>4 pièces</b></p>
            <hr>
            <h3 style="color: #EF4444; margin: 0;">180 000 €</h3>
        </div>
        """, unsafe_allow_html=True)
        
    with col_vs:
        st.markdown("""
        <div style="text-align: center; padding-top: 40px;">
            <span style="font-size: 2.5rem; font-weight: bold; color: #9CA3AF;">VS</span>
            <br><br>
            <span style="font-size: 2rem;">❓</span>
            <b style="display:block; margin-top:5px;">Pourquoi ?</b>
        </div>
        """, unsafe_allow_html=True)
        
    with col_bienB:
        st.markdown("""
        <div style="background-color: rgba(0,0,0,0.02); padding: 20px; border-radius: 8px; border-left: 5px solid #10B981; text-align: center;">
            <span style="font-size: 3rem;">🏠</span>
            <h4>Bien B</h4>
            <p>📐 <b>100 m²</b><br>🚪 <b>4 pièces</b></p>
            <hr>
            <h3 style="color: #10B981; margin: 0;">420 000 €</h3>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-top: 25px; padding: 10px; background-color: #EFF6FF; border-radius: 8px;">
        <p style="font-size: 1.1rem; color: #1E40AF; margin: 0; font-weight: 500;">
            💡 <b>Parce que la valeur immobilière dépend autant du territoire que du logement lui-même.</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 3. LES DEUX AXES DU PROJET
# ==========================================
st.markdown("## ⚔️ Les deux axes stratégiques")

col_axe1, col_axe2 = st.columns(2)

with col_axe1:
    with st.container(border=True):
        st.markdown("### 🗺️ Axe Territorial")
        st.markdown("*Comprendre l'attractivité d'une commune*")
        
        st.caption("Critères analysés :")
        st.markdown("""
        - 🏢 **Immobilier** (Dynamique locale)
        - 👥 **Population** (Démographie)
        - 💰 **Revenus** (Niveau de vie Filosofi)
        - 🏫 **Équipements** (BPE, commerces, écoles)
        - 🚇 **Transports** (Accessibilité)
        - 🛡️ **Sécurité** (Criminalité et faits constatés)
        """)
        
        st.markdown("""
        <div style="background-color: #EEF2F6; padding: 12px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #3B82F6;">
            <b>🚀 Résultat :</b> Score territorial multicritère
        </div>
        """, unsafe_allow_html=True)

with col_axe2:
    with st.container(border=True):
        st.markdown("### 🤖 Axe Prédictif")
        st.markdown("*Estimer la valeur d'un bien immobilier*")
        
        st.caption("Variables d'entrée du modèle :")
        st.markdown("""
        - 📏 **Caractéristiques du bien** (Surface, pièces...)
        - 🌳 **Environnement local** (Proximité des services)
        - 📈 **Données socio-économiques** (Richesse commune)
        - ⚡ **Données énergétiques** (DPE du logement)
        - <br> - <br> """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #EEF2F6; padding: 12px; border-radius: 6px; margin-top: 15px; border-left: 4px solid #10B981;">
            <b>🔮 Résultat :</b> Estimation intelligente du prix
        </div>
        """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 4. LES CHIFFRES CLÉS (KPI)
# ==========================================
st.markdown("## 📊 Le projet en chiffres")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Transactions analysées", value="20 M+")
with kpi2:
    st.metric(label="Sources fusionnées", value="6")
with kpi3:
    st.metric(label="Variables enrichies", value="68")
with kpi4:
    st.metric(label="Modèles spécialisés", value="6")

st.write("---")


# ==========================================
# 5. LES PERSONAS
# ==========================================
st.markdown("## 👥 À qui s'adresse cette plateforme ?")

pers1, pers2, pers3, pers4 = st.columns(4)

with pers1:
    with st.container(border=True):
        st.markdown("#### 👨‍👩‍👧 Particulier")
        st.caption("Comparer plusieurs communes cibles avant un achat immobilier.")

with pers2:
    with st.container(border=True):
        st.markdown("#### 🏠 Investisseur")
        st.caption("Identifier des zones à fort potentiel et sous-évaluées.")

with pers3:
    with st.container(border=True):
        st.markdown("#### 🧑‍💼 Professionnel")
        st.caption("Aider à l'estimation de biens et optimiser la prospection.")

with pers4:
    with st.container(border=True):
        st.markdown("#### 🏛️ Collectivité")
        st.caption("Comprendre finement les dynamiques de son territoire.")

st.write("---")


# ==========================================
# 6. LES DONNÉES UTILISÉES (Pipeline horizontal)
# ==========================================
st.markdown("## 🧬 Architecture des données")

col_d1, arr1, col_d2, arr2, col_d3 = st.columns([5, 1, 4, 1, 4])

with col_d1:
    st.markdown("""
    <div style="display: grid; gap: 8px;">
        <span style="background:#3B82F6; color:white; padding:6px; border-radius:4px; text-align:center; font-weight:bold; font-size:0.9rem;">📦 DVF (Demandes de Valeurs Foncières)</span>
        <span style="background:#4B5563; color:white; padding:6px; border-radius:4px; text-align:center; font-weight:bold; font-size:0.9rem;">👥 INSEE Population</span>
        <span style="background:#4B5563; color:white; padding:6px; border-radius:4px; text-align:center; font-weight:bold; font-size:0.9rem;">💰 Filosofi (Revenus)</span>
        <span style="background:#4B5563; color:white; padding:6px; border-radius:4px; text-align:center; font-weight:bold; font-size:0.9rem;">🏫 BPE (Équipements)</span>
        <span style="background:#4B5563; color:white; padding:6px; border-radius:4px; text-align:center; font-weight:bold; font-size:0.9rem;">🛡️ Criminalité / Sécurité</span>
        <span style="background:#4B5563; color:white; padding:6px; border-radius:4px; text-align:center; font-weight:bold; font-size:0.9rem;">⚡ DPE (Performance Énergétique)</span>
    </div>
    """, unsafe_allow_html=True)

with arr1:
    st.markdown("<h2 style='text-align: center; margin-top: 60px; color:#9CA3AF;'>➡</h2>", unsafe_allow_html=True)

with col_d2:
    st.markdown("""
    <div style="background: #10B981; color: white; padding: 45px 15px; border-radius: 8px; text-align: center; margin-top: 30px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        🔄<br><br>Fusion Multi-Sources<br>&amp; Géocodage
    </div>
    """, unsafe_allow_html=True)

with arr2:
    st.markdown("<h2 style='text-align: center; margin-top: 60px; color:#9CA3AF;'>➡</h2>", unsafe_allow_html=True)

with col_d3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A, #3B82F6); color: white; padding: 45px 15px; border-radius: 8px; text-align: center; margin-top: 30px; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        🚀<br><br>Compagnon Immobilier
    </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 7. TIMELINE DU PROJET
# ==========================================
st.markdown("## ⏳ Fil conducteur du projet")

t1, t2, t3, t4 = st.columns(4)

with t1:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">🔍</span>
        <h4 style="margin: 10px 0 5px 0; color:#3B82F6;">1. EDA</h4>
        <small style="color:#6B7280;">Exploration & Analyse des anomalies</small>
    </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">🛠️</span>
        <h4 style="margin: 10px 0 5px 0; color:#F59E0B;">2. Préparation</h4>
        <small style="color:#6B7280;">Nettoyage, Fusion & Feature Engineering</small>
    </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">🧠</span>
        <h4 style="margin: 10px 0 5px 0; color:#10B981;">3. Modélisation</h4>
        <small style="color:#6B7280;">Entraînement des modèles spécialisés</small>
    </div>
    """, unsafe_allow_html=True)

with t4:
    st.markdown("""
    <div class="timeline-step">
        <span style="font-size: 2rem;">💻</span>
        <h4 style="margin: 10px 0 5px 0; color:#8B5CF6;">4. Application</h4>
        <small style="color:#6B7280;">Déploiement de l'outil d'aide à la décision</small>
    </div>
    """, unsafe_allow_html=True)

st.write("---")


# ==========================================
# 8. TRANSITION FINALE - MODIFIÉE (Titre en blanc)
# ==========================================
st.markdown("""
<div style="background-color: #111827; color: white; padding: 30px; border-radius: 8px; border-left: 6px solid #3B82F6; margin-top: 20px;">
    <h3 style="color: #FFFFFF; margin-top: 0; font-weight: 700;">💡 Avant de construire une IA, il faut comprendre la donnée.</h3>
    <p style="margin-bottom: 0; opacity: 0.9; line-height: 1.6;">
        Plus de <b>20 millions de transactions immobilières</b> cachent de nombreuses anomalies, incohérences et disparités territoriales. 
        La première étape consiste donc à explorer cette matière première et à comprendre les mécanismes du marché immobilier français.
    </p>
</div>
""", unsafe_allow_html=True)
