"""
🔧 Configuration FraudGuard AI
Configuration centralisée pour tous les composants
"""

import os
from pathlib import Path

# ===== PATHS =====
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

# Créer les dossiers si nécessaire
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ===== DATABASE =====
DATABASE_URL = "sqlite:///fraudguard.db"
TRANSACTIONS_FILE = str(DATA_DIR / "transactions.csv")  # String pour compatibilité pandas

# ===== API CONFIGURATION =====
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "FraudGuard AI API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
🛡️ **FraudGuard AI** - Système de détection de fraude temps réel

## Fonctionnalités
- Scoring fraude en temps réel (< 100ms)
- Modèles ML hybrides (XGBoost + Isolation Forest)
- Métriques business en temps réel
- Interface REST simple et efficace

## Endpoints principaux
- `/predict` : Scoring d'une transaction
- `/batch-predict` : Scoring multiple
- `/metrics` : Métriques système
- `/health` : Status de l'API
"""

# ===== ML CONFIGURATION =====
MODEL_PATH = str(MODELS_DIR / "fraud_detector.pkl")  # String pour compatibilité pickle
FEATURES = [
    'amount', 'hour', 'day_of_week', 'merchant_category',
    'user_age', 'account_age_days', 'transaction_count_day',
    'amount_last_hour', 'amount_last_day', 'velocity_1h',
    'avg_amount_30d', 'std_amount_30d', 'geographic_risk',
    'device_risk', 'time_since_last_transaction'
]

# Seuils de détection
FRAUD_THRESHOLD_HIGH = 0.8   # Blocage immédiat
FRAUD_THRESHOLD_MEDIUM = 0.5 # Alerte
FRAUD_THRESHOLD_LOW = 0.2    # Surveillance

# ===== DATA GENERATION =====
N_TRANSACTIONS = 10000  # Nombre de transactions à générer
FRAUD_RATE = 0.02       # 2% de fraudes (réaliste)

# Configuration pour générateur (compatibilité avec code existant)
DATA_CONFIG = {
    'num_transactions': N_TRANSACTIONS,
    'fraud_rate': FRAUD_RATE,
    'num_days': 30
}

# ===== DASHBOARD CONFIGURATION =====
DASHBOARD_PORT = 8502  # Garder 8502 pour compatibilité avec le code existant
DASHBOARD_TITLE = "🛡️ FraudGuard AI - Dashboard"
UPDATE_INTERVAL = 5    # Secondes entre les mises à jour

# Configuration Streamlit (compatibilité)
STREAMLIT_CONFIG = {
    'page_title': DASHBOARD_TITLE,
    'page_icon': "🛡️",
    'layout': "wide"
}

# ===== MONITORING =====
LOG_LEVEL = "INFO"
METRICS_ENABLED = True

# ===== BUSINESS KPIS =====
TARGET_PRECISION = 0.95     # 95% de précision
TARGET_RECALL = 0.90        # 90% de rappel
TARGET_LATENCY = 100        # < 100ms
MAX_FALSE_POSITIVE = 0.05   # < 5% faux positifs

# ===== SIMULATION PARAMETERS =====
# Pour la demo en temps réel
SIMULATION_SPEED = 1.0      # Vitesse de simulation (1.0 = temps réel)
TRANSACTIONS_PER_SECOND = 10 # Débit de transactions

# ===== FEATURE ENGINEERING =====
CATEGORICAL_FEATURES = ['merchant_category', 'device_type', 'payment_method']
NUMERICAL_FEATURES = ['amount', 'user_age', 'account_age_days']
TEMPORAL_FEATURES = ['hour', 'day_of_week', 'month']

# ===== MODEL PARAMETERS =====
XGBOOST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1,
    'random_state': 42,
    'eval_metric': 'auc'
}

ISOLATION_FOREST_PARAMS = {
    'contamination': 0.02,  # 2% de contamination
    'random_state': 42,
    'n_estimators': 100
}

# Configuration modèle (compatibilité)
MODEL_CONFIG = {
    'n_estimators': XGBOOST_PARAMS['n_estimators'],
    'max_depth': XGBOOST_PARAMS['max_depth'],
    'learning_rate': XGBOOST_PARAMS['learning_rate'],
    'random_state': XGBOOST_PARAMS['random_state']
}

# ===== PERFORMANCE MONITORING =====
PERFORMANCE_WINDOW = 1000  # Nombre de prédictions pour calcul métriques
ALERT_THRESHOLDS = {
    'precision_drop': 0.90,     # Alerte si précision < 90%
    'latency_spike': 200,       # Alerte si latence > 200ms
    'error_rate': 0.01,         # Alerte si taux erreur > 1%
    'memory_usage': 0.80        # Alerte si mémoire > 80%
}

# ===== DEMO CONFIGURATION =====
DEMO_MODE = True                # Active les fonctionnalités de démonstration
DEMO_DATA_SIZE = 1000          # Nombre de transactions pour la démo
REAL_TIME_SIMULATION = True    # Simulation temps réel pour dashboard

# ===== URL ET ENDPOINTS =====
API_BASE_URL = f"http://localhost:{API_PORT}"
DASHBOARD_URL = f"http://localhost:{DASHBOARD_PORT}"

# Endpoints principaux
ENDPOINTS = {
    'predict': f"{API_BASE_URL}/predict",
    'batch': f"{API_BASE_URL}/batch-predict",
    'metrics': f"{API_BASE_URL}/metrics",
    'health': f"{API_BASE_URL}/health",
    'simulate': f"{API_BASE_URL}/simulate-transaction"
}

# ===== LOGGING CONFIGURATION =====
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': str(PROJECT_ROOT / 'fraudguard.log'),
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': LOG_LEVEL,
            'propagate': False
        }
    }
}

# ===== MESSAGES DE DÉMARRAGE =====
def print_startup_info():
    """Affiche les informations de démarrage"""
    print("=" * 60)
    print("🛡️  FRAUDGUARD AI - CONFIGURATION CHARGÉE")
    print("=" * 60)
    print(f"📊 Données: {DATA_DIR}")
    print(f"🤖 Modèles: {MODELS_DIR}")
    print(f"🌐 API: {API_BASE_URL}")
    print(f"📈 Dashboard: {DASHBOARD_URL}")
    print(f"🎯 Mode: {'DEMO' if DEMO_MODE else 'PRODUCTION'}")
    print(f"📋 Features: {len(FEATURES)} variables")
    print(f"⚡ Objectif latence: < {TARGET_LATENCY}ms")
    print(f"🎯 Objectif précision: {TARGET_PRECISION:.1%}")
    print("=" * 60)

# Auto-exécution des messages de démarrage
if __name__ != "__main__":  # Ne pas afficher lors d'import direct
    print_startup_info()
else:
    print(f"✅ Configuration FraudGuard AI chargée")
    print(f"📊 Données: {DATA_DIR}")
    print(f"🤖 Modèles: {MODELS_DIR}")
    print(f"🌐 API: http://localhost:{API_PORT}")
    print(f"📈 Dashboard: http://localhost:{DASHBOARD_PORT}")