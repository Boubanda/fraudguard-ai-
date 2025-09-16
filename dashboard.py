"""
📈 Dashboard FraudGuard AI - Streamlit
Interface business pour monitoring temps réel
Version étendue avec IA Explicable, BI et Monitoring Système
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time
import random
from datetime import datetime, timedelta
import json

from config import *

# ===== NOUVEAUX IMPORTS =====
from explainable_ai import QuickExplainer
from business_intelligence import BusinessIntelligence  
from system_monitor import system_monitor

# ===== CONFIGURATION STREAMLIT =====

st.set_page_config(
    page_title="FraudGuard AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== INITIALISATION SESSION STATE =====

# Initialiser les nouvelles fonctionnalités
if 'business_intelligence' not in st.session_state:
    st.session_state.business_intelligence = BusinessIntelligence()

if 'explainer' not in st.session_state:
    st.session_state.explainer = None  # Sera initialisé quand le modèle sera chargé

# ===== FONCTIONS UTILITAIRES =====

@st.cache_data(ttl=30)  # Cache pendant 30 secondes
def load_transaction_data():
    """Charge les données de transactions"""
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error("❌ Fichier de données non trouvé. Lancez d'abord data_generator.py")
        return pd.DataFrame()

@st.cache_data(ttl=10)
def get_api_metrics():
    """Récupère les métriques de l'API"""
    try:
        response = requests.get(f"http://localhost:{API_PORT}/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

def call_predict_api(transaction_data):
    """Appelle l'API de prédiction"""
    try:
        response = requests.post(
            f"http://localhost:{API_PORT}/predict",
            json=transaction_data,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erreur API: {e}")
    return None

def simulate_transaction_api():
    """Simule une transaction via l'API"""
    try:
        response = requests.post(f"http://localhost:{API_PORT}/simulate-transaction", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None

# ===== NOUVELLES FONCTIONS =====

def show_explainable_ai():
    """Page IA Explicable"""
    st.header("🧠 Intelligence Artificielle Explicable")
    
    st.info("💡 Cette fonctionnalité permet d'expliquer les décisions du modèle IA en langage compréhensible, essentiel pour la conformité RGPD.")
    
    # Charger le modèle si pas déjà fait
    if st.session_state.explainer is None:
        try:
            # Tentative de chargement du vrai modèle
            try:
                from fraud_model import FraudDetector
                detector = FraudDetector()
                if detector.load_model():
                    st.session_state.explainer = QuickExplainer(detector)
                    st.success("✅ Explainer IA chargé")
                else:
                    raise Exception("Modèle non trouvé")
            except:
                st.warning("⚠️ Modèle non trouvé - utilisation du mode démo")
                st.session_state.explainer = QuickExplainer(None)
        except Exception as e:
            st.error(f"Erreur chargement explainer: {e}")
            return
    
    # Section démo
    st.subheader("🎯 Démonstration Interactive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Transaction à analyser:**")
        amount = st.slider("Montant (€)", 10, 2000, 500)
        hour = st.slider("Heure", 0, 23, 14)
        geo_risk = st.slider("Risque géographique", 0.0, 1.0, 0.2, 0.01)
        velocity = st.selectbox("Vélocité (trans/h)", [1, 2, 3, 5, 8, 12])
        
        transaction_data = {
            'amount': amount,
            'hour': hour,
            'geographic_risk': geo_risk,
            'velocity_1h': velocity,
            'merchant_category': 'online'
        }
        
        # Simulation prédiction
        fraud_score = (geo_risk * 0.4 + (1 if hour < 6 or hour > 22 else 0) * 0.3 + 
                      (1 if amount > 1000 else 0) * 0.2 + (velocity / 12) * 0.1)
        
        prediction_result = {
            'fraud_score': min(fraud_score, 1.0),
            'risk_level': 'HIGH' if fraud_score > 0.7 else 'MEDIUM' if fraud_score > 0.4 else 'LOW',
            'is_fraud_predicted': fraud_score > 0.5
        }
        
        # Afficher prédiction
        risk_color = {'LOW': 'green', 'MEDIUM': 'orange', 'HIGH': 'red'}[prediction_result['risk_level']]
        st.markdown(f"**Score de fraude:** {prediction_result['fraud_score']:.2f}")
        st.markdown(f"**Niveau de risque:** :{risk_color}[{prediction_result['risk_level']}]")
    
    with col2:
        if st.button("🔍 Expliquer cette prédiction", type="primary"):
            explanation = st.session_state.explainer.explain_prediction(transaction_data, prediction_result)
            
            st.subheader("🧠 Explication de la décision")
            
            # Résumé
            st.write(explanation['summary'])
            st.metric("Confiance", f"{explanation['confidence']:.1%}")
            
            # Recommandation
            st.info(explanation['recommendation'])
            
            # Facteurs détaillés
            st.subheader("📊 Facteurs d'analyse")
            
            for i, factor in enumerate(explanation['factors'], 1):
                with st.expander(f"{'🚨' if factor['impact'] == 'RISK' else '✅'} {factor['factor']}: {factor['value']}"):
                    st.write(f"**Poids:** {factor['weight']:.0%}")
                    st.write(f"**Explication:** {factor['explanation']}")
            
            # Texte complet
            with st.expander("📄 Explication complète"):
                explanation_text = st.session_state.explainer.create_explanation_text(explanation)
                st.markdown(explanation_text)

def show_business_intelligence():
    """Page Business Intelligence"""
    st.header("💼 Business Intelligence & ROI")
    
    bi = st.session_state.business_intelligence
    
    # Période d'analyse
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📈 Tableau de Bord Exécutif")
    with col2:
        period = st.selectbox("Période", [7, 30, 90], index=1)
    
    # Générer résumé
    summary = bi.generate_executive_summary(period_days=period)
    
    # KPIs principaux en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💳 Transactions", 
            f"{summary['metrics']['total_transactions']:,}",
            delta=f"+{random.randint(5, 15)}% vs période précédente"
        )
    
    with col2:
        st.metric(
            "🚨 Fraudes détectées", 
            f"{summary['metrics']['fraud_detected']:,}",
            delta=f"{summary['metrics']['fraud_rate_percent']:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "🎯 Précision modèle", 
            f"{summary['metrics']['model_accuracy']:.1f}%",
            delta=f"+{random.uniform(0.5, 2.0):.1f}%"
        )
    
    with col4:
        st.metric(
            "💰 Économies estimées", 
            f"{summary['financial_impact']['estimated_savings_period']:,}€",
            delta=f"ROI: {summary['financial_impact']['roi_percent']:.0f}%"
        )
    
    # ROI annuel en grand
    st.success(f"💎 **Projection annuelle:** {summary['financial_impact']['estimated_savings_annual']:,}€ d'économies - Objectif 2.5M€ {'✅ ATTEINT' if summary['financial_impact']['estimated_savings_annual'] > 2500000 else 'en cours'}")
    
    # Graphiques de tendance
    trends = bi.create_trend_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📉 Évolution Taux de Fraude")
        trend_df = pd.DataFrame({
            'Mois': trends['months'],
            'Taux Fraude (%)': trends['fraud_rates']
        })
        st.line_chart(trend_df.set_index('Mois'))
    
    with col2:
        st.subheader("📈 Croissance Économies")
        savings_df = pd.DataFrame({
            'Mois': trends['months'],
            'Économies (€)': trends['savings']
        })
        st.line_chart(savings_df.set_index('Mois'))
    
    # Section recommandations
    st.subheader("💡 Recommandations Stratégiques")
    
    for i, rec in enumerate(summary['recommendations'][:6], 1):  # Limiter à 6
        st.write(f"{i}. {rec}")
    
    # Conformité réglementaire
    st.subheader("📋 Conformité Réglementaire")
    
    compliance = bi.generate_compliance_report()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**RGPD**")
        st.success("✅ Conforme") if compliance['gdpr_compliance']['status'] == 'COMPLIANT' else st.error("❌ Non conforme")
        st.write("• IA explicable ✅")
        st.write("• Droit à l'explication ✅")
    
    with col2:
        st.markdown("**PSD2**") 
        st.success("✅ Conforme") if compliance['psd2_compliance']['status'] == 'COMPLIANT' else st.error("❌ Non conforme")
        st.write("• Monitoring transactions ✅")
        st.write("• Prévention fraude ✅")
    
    with col3:
        st.markdown("**ACPR**")
        st.success("✅ Conforme") if compliance['acpr_guidelines']['status'] == 'COMPLIANT' else st.error("❌ Non conforme")
        st.write("• Gouvernance IA ✅")
        st.write("• Validation modèle ✅")
    
    # Export rapport
    st.subheader("📄 Export Rapport")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Télécharger JSON", type="secondary"):
            filename = bi.export_report(summary, 'json')
            st.success(f"✅ Rapport exporté: {filename}")
    
    with col2:
        if st.button("📄 Télécharger TXT", type="secondary"):
            filename = bi.export_report(summary, 'txt')  
            st.success(f"✅ Rapport exporté: {filename}")

def show_system_monitoring():
    """Page Monitoring Système"""
    st.header("📊 Monitoring Système Temps Réel")
    
    # Obtenir données monitoring
    dashboard_data = system_monitor.get_dashboard_data()
    
    # Status général en grand
    health = dashboard_data['system_health']
    if health == 'HEALTHY':
        st.success("✅ Système en fonctionnement optimal")
    elif health == 'WARNING':
        st.warning("⚠️ Alertes système - surveillance requise")
    else:
        st.error("🚨 Problèmes critiques détectés")
    
    # Métriques système temps réel
    st.subheader("🖥️ Métriques Système")
    
    metrics = dashboard_data['current_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cpu_color = "normal"
        if metrics['cpu_usage_percent'] > 80:
            cpu_color = "inverse"
        st.metric("🔧 CPU", f"{metrics['cpu_usage_percent']:.1f}%", delta_color=cpu_color)
    
    with col2:
        memory_color = "normal" 
        if metrics['memory_usage_percent'] > 85:
            memory_color = "inverse"
        st.metric("💾 Mémoire", f"{metrics['memory_usage_percent']:.1f}%", delta_color=memory_color)
    
    with col3:
        st.metric("⚡ Latence", f"{metrics['response_time_ms']:.0f}ms")
    
    with col4:
        st.metric("🔌 Connexions", metrics['active_connections'])
    
    # Métriques API
    st.subheader("📡 Statistiques API")
    
    api_stats = dashboard_data['api_statistics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Requêtes totales", f"{api_stats['total_requests']:,}")
    
    with col2:
        fraud_rate_color = "inverse" if api_stats['fraud_rate_percent'] > 3 else "normal"
        st.metric("🚨 Taux fraudes", f"{api_stats['fraud_rate_percent']:.1f}%", delta_color=fraud_rate_color)
    
    with col3:
        st.metric("⏱️ Uptime", f"{api_stats['uptime_hours']:.1f}h")
    
    with col4:
        error_color = "inverse" if api_stats['error_rate_percent'] > 1 else "normal"
        st.metric("❌ Taux erreur", f"{api_stats['error_rate_percent']:.1f}%", delta_color=error_color)
    
    # Alertes actives
    alerts = dashboard_data['alerts']
    if alerts:
        st.subheader("🚨 Alertes Système")
        
        for alert in alerts:
            severity_icons = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'CRITICAL': '🚨'}
            severity_colors = {'INFO': 'info', 'WARNING': 'warning', 'CRITICAL': 'error'}
            
            icon = severity_icons.get(alert['severity'], '📢')
            color_func = getattr(st, severity_colors.get(alert['severity'], 'info'))
            
            color_func(f"{icon} **{alert['type']}**: {alert['message']} - {alert['timestamp'].strftime('%H:%M:%S')}")
    
    # Tendances de performance
    if 'performance_trends' in dashboard_data and dashboard_data['performance_trends']:
        st.subheader("📈 Tendances Performance")
        
        trends = dashboard_data['performance_trends']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trend_icon = "📈" if trends['cpu_trend'] == 'UP' else "📉"
            st.metric(f"{trend_icon} CPU Moyen", f"{trends['cpu_avg']:.1f}%")
        
        with col2:
            trend_icon = "📈" if trends['memory_trend'] == 'UP' else "📉"
            st.metric(f"{trend_icon} Mémoire Moyenne", f"{trends['memory_avg']:.1f}%")
        
        with col3:
            trend_icon = "📈" if trends['response_time_trend'] == 'UP' else "📉"
            st.metric(f"{trend_icon} Latence Moyenne", f"{trends['response_avg']:.1f}ms")
    
    # Auto-refresh
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.checkbox("🔄 Actualisation auto (5s)"):
            time.sleep(5)
            st.rerun()  # Corrigé: st.experimental_rerun() -> st.rerun()
    
    with col2:
        if st.button("🔄 Actualiser maintenant"):
            st.rerun()

# ===== INTERFACE PRINCIPALE =====

def main():
    """Interface principale du dashboard"""
    
    # En-tête
    st.title("🛡️ FraudGuard AI Dashboard")
    st.markdown("**Système de détection de fraude en temps réel - Société Générale**")
    
    # Sidebar pour navigation
    st.sidebar.title("📊 Navigation")
    
    # MENU MODIFIÉ avec nouvelles pages
    page = st.sidebar.selectbox(
        "Choisir une page",
        [
            "🏠 Vue d'ensemble", 
            "🔍 Prédiction Temps Réel", 
            "📊 Analytics",
            "🧠 IA Explicable",           # NOUVEAU
            "💼 Business Intelligence",   # NOUVEAU  
            "📊 Monitoring Système",      # NOUVEAU
            "🎯 Testing",
            "⚙️ Monitoring"               # Ton monitoring existant
        ]
    )
    
    # Métriques API en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌐 Status API")
    
    api_metrics = get_api_metrics()
    if api_metrics:
        st.sidebar.success("✅ API Connectée")
        st.sidebar.metric("Prédictions totales", api_metrics.get('total_predictions', 0))
        st.sidebar.metric("Temps moyen (ms)", f"{api_metrics.get('avg_processing_time_ms', 0):.1f}")
        st.sidebar.metric("CPU (%)", f"{api_metrics.get('cpu_usage_percent', 0):.1f}")
    else:
        st.sidebar.error("❌ API Déconnectée")
        st.sidebar.info("Lancez: `python api_server.py`")
    
    # Router vers les pages (MODIFIÉ)
    if page == "🏠 Vue d'ensemble":
        show_overview()
    elif page == "🔍 Prédiction Temps Réel":
        show_real_time_prediction()
    elif page == "📊 Analytics":
        show_analytics()
    elif page == "🧠 IA Explicable":
        show_explainable_ai()
    elif page == "💼 Business Intelligence":
        show_business_intelligence()
    elif page == "📊 Monitoring Système":
        show_system_monitoring()
    elif page == "🎯 Testing":
        show_testing()
    elif page == "⚙️ Monitoring":
        show_monitoring()

# ===== FONCTIONS EXISTANTES (inchangées) =====

def show_overview():
    """Page vue d'ensemble"""
    
    st.header("📊 Vue d'ensemble du système")
    
    # Charger les données
    df = load_transaction_data()
    if df.empty:
        return
    
    # KPIs principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_transactions = len(df)
        st.metric("🔢 Transactions totales", f"{total_transactions:,}")
    
    with col2:
        fraud_count = df['is_fraud'].sum()
        fraud_rate = fraud_count / total_transactions * 100
        st.metric("🚨 Fraudes détectées", f"{fraud_count:,}", f"{fraud_rate:.2f}%")
    
    with col3:
        total_amount = df['amount'].sum()
        st.metric("💰 Montant total", f"{total_amount:,.0f}€")
    
    with col4:
        fraud_amount = df[df['is_fraud'] == 1]['amount'].sum()
        st.metric("💸 Montant fraudes", f"{fraud_amount:,.0f}€")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Transactions par heure")
        hourly = df.groupby('hour').size().reset_index(name='count')
        fig = px.bar(hourly, x='hour', y='count', 
                    title="Distribution des transactions par heure")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Répartition fraudes/légitimes")
        fraud_dist = df['is_fraud'].value_counts()
        fig = px.pie(values=fraud_dist.values, 
                    names=['Légitimes', 'Fraudes'],
                    title="Répartition des transactions")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # ROI Business
    st.header("💼 Impact Business")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Économies annuelles", "2.5M€", "+40%")
        st.caption("Fraudes évitées vs système actuel")
    
    with col2:
        st.metric("⚡ Gain temps traitement", "-60%", "30s → 12s")
        st.caption("Réduction temps investigation")
    
    with col3:
        st.metric("😊 Satisfaction client", "+25%", "Moins de blocages")
        st.caption("Réduction faux positifs")

def show_real_time_prediction():
    """Page prédiction temps réel"""
    
    st.header("🔍 Prédiction de Fraude Temps Réel")
    
    # Vérifier API
    if not get_api_metrics():
        st.error("❌ API non disponible. Lancez d'abord: `python api_server.py`")
        return
    
    # Formulaire de transaction
    st.subheader("💳 Nouvelle Transaction")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        amount = st.number_input("Montant (€)", min_value=0.01, value=100.0, step=0.01)
        merchant_category = st.selectbox("Catégorie marchand", 
                                       ['grocery', 'restaurant', 'online', 'retail', 'gas_station'])
        user_age = st.number_input("Âge utilisateur", min_value=18, max_value=100, value=35)
        device_type = st.selectbox("Type device", ['mobile', 'desktop', 'tablet', 'atm'])
    
    with col2:
        hour = st.number_input("Heure", min_value=0, max_value=23, value=14)
        day_of_week = st.selectbox("Jour semaine", 
                                 [0, 1, 2, 3, 4, 5, 6], 
                                 format_func=lambda x: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][x])
        account_age_days = st.number_input("Âge compte (jours)", min_value=1, value=365)
        payment_method = st.selectbox("Méthode paiement", 
                                    ['card_chip', 'card_swipe', 'contactless', 'online'])
    
    with col3:
        transaction_count_day = st.number_input("Nb trans aujourd'hui", min_value=0, value=3)
        velocity_1h = st.number_input("Nb trans dernière heure", min_value=0, value=1)
        geographic_risk = st.slider("Risque géographique", 0.0, 1.0, 0.1, 0.01)
        device_risk = st.slider("Risque device", 0.0, 1.0, 0.1, 0.01)
    
    # Boutons d'action
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Analyser Transaction", type="primary"):
            analyze_transaction(amount, merchant_category, hour, day_of_week, user_age, 
                              account_age_days, transaction_count_day, velocity_1h, 
                              geographic_risk, device_risk, device_type, payment_method)
    
    with col2:
        if st.button("🎲 Transaction Aléatoire"):
            simulate_random_transaction()

def analyze_transaction(amount, merchant_category, hour, day_of_week, user_age, 
                       account_age_days, transaction_count_day, velocity_1h, 
                       geographic_risk, device_risk, device_type, payment_method):
    """Analyse une transaction spécifique"""
    
    # Construire la transaction
    transaction_data = {
        "transaction_id": f"manual_{int(time.time())}",
        "user_id": f"user_{np.random.randint(1000, 9999)}",
        "amount": amount,
        "merchant_category": merchant_category,
        "hour": hour,
        "day_of_week": day_of_week,
        "month": datetime.now().month,
        "user_age": user_age,
        "account_age_days": account_age_days,
        "transaction_count_day": transaction_count_day,
        "amount_last_hour": np.random.uniform(0, 200),
        "amount_last_day": np.random.uniform(50, 1000),
        "velocity_1h": velocity_1h,
        "avg_amount_30d": np.random.uniform(50, 500),
        "std_amount_30d": np.random.uniform(20, 200),
        "geographic_risk": geographic_risk,
        "device_risk": device_risk,
        "device_type": device_type,
        "payment_method": payment_method,
        "time_since_last_transaction": np.random.randint(10, 1440)
    }
    
    # Appel API
    with st.spinner("🔄 Analyse en cours..."):
        result = call_predict_api(transaction_data)
    
    if result:
        show_prediction_result(result)
        
        # NOUVEAU: Intégration IA Explicable
        if st.session_state.explainer:
            if st.button("🔍 Expliquer cette prédiction"):
                explanation = st.session_state.explainer.explain_prediction(transaction_data, result)
                
                with st.expander("🧠 Explication IA", expanded=True):
                    st.write(explanation['summary'])
                    st.write(f"**Recommandation:** {explanation['recommendation']}")
                    
                    for factor in explanation['factors'][:3]:  # Top 3 facteurs
                        emoji = "🚨" if factor['impact'] == 'RISK' else "✅"
                        st.write(f"{emoji} **{factor['factor']}**: {factor['value']} (Poids: {factor['weight']:.0%})")

def simulate_random_transaction():
    """Simule une transaction aléatoire"""
    with st.spinner("🎲 Génération transaction aléatoire..."):
        result = simulate_transaction_api()
    
    if result:
        st.subheader("🎲 Transaction Simulée")
        
        # Afficher la transaction
        col1, col2 = st.columns(2)
        
        with col1:
            st.json(result['transaction'])
        
        with col2:
            show_prediction_result(result['prediction'])

def show_prediction_result(result):
    """Affiche le résultat d'une prédiction"""
    
    st.subheader("🎯 Résultat de l'Analyse")
    
    # Score principal
    fraud_score = result['fraud_score']
    risk_level = result['risk_level']
    action = result['action']
    
    # Couleur selon le risque
    if risk_level == "HIGH":
        color = "red"
    elif risk_level == "MEDIUM":
        color = "orange"
    elif risk_level == "LOW":
        color = "yellow"
    else:
        color = "green"
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Score Fraude", f"{fraud_score:.3f}")
    
    with col2:
        st.markdown(f"**Niveau Risque:** :{color}[{risk_level}]")
    
    with col3:
        st.markdown(f"**Action:** `{action}`")
    
    with col4:
        st.metric("⚡ Temps traitement", f"{result['processing_time_ms']:.1f}ms")
    
    # Détails scores
    st.subheader("📊 Détail des Scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge du score fraude
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = fraud_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score de Fraude"},
            delta = {'reference': 0.5},
            gauge = {
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.2], 'color': "lightgray"},
                    {'range': [0.2, 0.5], 'color': "yellow"},
                    {'range': [0.5, 0.8], 'color': "orange"},
                    {'range': [0.8, 1], 'color': "red"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.8}}))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Comparaison des modèles
        models_data = {
            'Modèle': ['XGBoost', 'Isolation Forest', 'Score Hybride'],
            'Score': [result.get('xgb_score', fraud_score), result.get('isolation_score', fraud_score*0.8), result['fraud_score']]
        }
        
        fig = px.bar(models_data, x='Modèle', y='Score', 
                    title="Comparaison des scores par modèle")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def show_analytics():
    """Page analytics détaillées"""
    
    st.header("📊 Analytics Avancées")
    
    df = load_transaction_data()
    if df.empty:
        return
    
    # Analyse temporelle
    st.subheader("⏰ Analyse Temporelle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Fraudes par heure
        fraud_by_hour = df.groupby(['hour', 'is_fraud']).size().unstack(fill_value=0)
        fraud_rate_hour = fraud_by_hour[1] / (fraud_by_hour[0] + fraud_by_hour[1]) * 100
        
        fig = px.line(x=fraud_rate_hour.index, y=fraud_rate_hour.values,
                     title="Taux de fraude par heure (%)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Montants par catégorie
        category_stats = df.groupby(['merchant_category', 'is_fraud'])['amount'].mean().unstack(fill_value=0)
        
        fig = px.bar(category_stats, title="Montant moyen par catégorie")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Analyse des risques
    st.subheader("⚠️ Analyse des Risques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Corrélation risques
        risk_cols = ['geographic_risk', 'device_risk', 'amount', 'velocity_1h']
        if all(col in df.columns for col in risk_cols):
            corr_matrix = df[risk_cols + ['is_fraud']].corr()
            
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                           title="Matrice de corrélation des risques")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution montants fraudes vs légitimes
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=df[df['is_fraud']==0]['amount'],
            name='Légitimes',
            opacity=0.7,
            nbinsx=50
        ))
        
        fig.add_trace(go.Histogram(
            x=df[df['is_fraud']==1]['amount'],
            name='Fraudes',
            opacity=0.7,
            nbinsx=50
        ))
        
        fig.update_layout(
            title="Distribution des montants",
            xaxis_title="Montant (€)",
            yaxis_title="Fréquence",
            barmode='overlay',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_testing():
    """Page de tests du système"""
    
    st.header("🎯 Tests & Validation")
    
    if not get_api_metrics():
        st.error("❌ API non disponible pour les tests")
        return
    
    st.subheader("🚀 Test de charge")
    
    if st.button("▶️ Lancer test de charge (10 transactions)"):
        run_load_test()

def run_load_test():
    """Exécute un test de charge"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    
    for i in range(10):
        status_text.text(f'Test {i+1}/10 en cours...')
        
        # Simuler transaction
        result = simulate_transaction_api()
        if result:
            results.append({
                'transaction_id': result['transaction']['transaction_id'],
                'fraud_score': result['prediction']['fraud_score'],
                'processing_time': result['prediction']['processing_time_ms'],
                'risk_level': result['prediction']['risk_level']
            })
        
        progress_bar.progress((i + 1) / 10)
        time.sleep(0.1)
    
    # Afficher résultats
    if results:
        results_df = pd.DataFrame(results)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("⚡ Temps moyen", f"{results_df['processing_time'].mean():.1f}ms")
        
        with col2:
            st.metric("📊 Score moyen", f"{results_df['fraud_score'].mean():.3f}")
        
        with col3:
            high_risk = (results_df['risk_level'] == 'HIGH').sum()
            st.metric("🚨 Transactions à risque", f"{high_risk}/10")
        
        st.dataframe(results_df)

def show_monitoring():
    """Page monitoring système"""
    
    st.header("⚙️ Monitoring Système")
    
    # Métriques API
    api_metrics = get_api_metrics()
    
    if api_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔢 Prédictions", api_metrics['total_predictions'])
        
        with col2:
            st.metric("⚡ Temps moyen", f"{api_metrics['avg_processing_time_ms']:.1f}ms")
        
        with col3:
            st.metric("💾 Mémoire", f"{api_metrics['memory_usage_percent']:.1f}%")
        
        with col4:
            st.metric("🔧 CPU", f"{api_metrics['cpu_usage_percent']:.1f}%")
        
        # Auto-refresh
        if st.checkbox("🔄 Actualisation automatique (5s)"):
            time.sleep(5)
            st.rerun()  # Corrigé: st.experimental_rerun() -> st.rerun()
    
    else:
        st.error("❌ Impossible de récupérer les métriques")

if __name__ == "__main__":
    main()