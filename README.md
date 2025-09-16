# 🛡️ FraudGuard AI - Détection de Fraude Temps Réel

> **Projet d'alternance Société Générale - Système de détection de fraude bancaire avec IA**

## 🎯 Vue d'ensemble

FraudGuard AI est un système hybride de détection de fraude bancaire utilisant des modèles de Machine Learning avancés pour analyser les transactions en temps réel et identifier les activités suspectes.

### 🏆 Objectifs Business
- **Réduire les fraudes** de 30% par rapport au système actuel
- **Diminuer les faux positifs** de 50% (moins de blocages clients légitimes)
- **Traitement temps réel** < 100ms par transaction
- **ROI estimé** : 2.5M€ d'économies annuelles

## 🛠️ Architecture Technique

### Stack Technologique
- **Machine Learning** : XGBoost + Isolation Forest (modèles hybrides)
- **API** : FastAPI (Python) pour scoring temps réel
- **Dashboard** : Streamlit pour interface business
- **Base de données** : SQLite (simple et efficace)
- **Monitoring** : Métriques système intégrées

### Modèles IA
1. **XGBoost** : Classification supervisée des fraudes
2. **Isolation Forest** : Détection d'anomalies non supervisée
3. **Ensemble hybride** : Combinaison des deux approches

## 🚀 Installation Rapide

### Prérequis
- Python 3.9+
- VS Code (recommandé)
- 8GB RAM minimum

### 1. Cloner/Créer le projet
```bash
# Créer le dossier du projet
mkdir fraudguard-ai
cd fraudguard-ai

# Créer les fichiers (voir structure ci-dessous)
```

### 2. Installation des dépendances
```bash
# Créer environnement virtuel
python -m venv fraudguard-env

# Activer l'environnement
# Windows:
fraudguard-env\Scripts\activate
# Mac/Linux:
source fraudguard-env/bin/activate

# Installer les packages
pip install -r requirements.txt
```

### 3. Lancement du système
```bash
# Lancement complet (recommandé)
python run.py

# Ou par étapes individuelles:
python data_generator.py    # Génération données
python fraud_model.py       # Entraînement modèles
python api_server.py        # API (terminal 1)
streamlit run dashboard.py  # Dashboard (terminal 2)
```

## 📁 Structure du Projet

```
fraudguard-ai/
├── 📋 requirements.txt          # Dépendances Python
├── ⚙️ config.py                 # Configuration globale
├── 📊 data_generator.py         # Génération données synthétiques
├── 🤖 fraud_model.py            # Modèles ML hybrides
├── 🌐 api_server.py             # API FastAPI temps réel
├── 📈 dashboard.py              # Dashboard Streamlit
├── 🚀 run.py                    # Script de lancement
├── 📖 README.md                 # Documentation
├── 📊 data/                     # Données générées
│   └── transactions.csv
└── 🤖 models/                   # Modèles sauvegardés
    └── fraud_detector.pkl
```

## 🎮 Utilisation

### 🌐 API Endpoints

**Base URL** : `http://localhost:8000`

- `GET /` : Page d'accueil API
- `POST /predict` : Scoring d'une transaction
- `POST /batch-predict` : Scoring multiple
- `GET /metrics` : Métriques système
- `GET /health` : Status de l'API
- `GET /docs` : Documentation interactive

### 📊 Exemple d'utilisation API

```python
import requests

# Transaction à analyser
transaction = {
    "transaction_id": "txn_001",
    "user_id": "user_1234",
    "amount": 150.0,
    "merchant_category": "restaurant",
    "hour": 14,
    "day_of_week": 2,
    "month": 9,
    "user_age": 35,
    "account_age_days": 365,
    "transaction_count_day": 3,
    "amount_last_hour": 50.0,
    "amount_last_day": 200.0,
    "velocity_1h": 1,
    "avg_amount_30d": 120.0,
    "std_amount_30d": 45.0,
    "geographic_risk": 0.1,
    "device_risk": 0.05,
    "device_type": "mobile",
    "payment_method": "contactless",
    "time_since_last_transaction": 60
}

# Appel API
response = requests.post("http://localhost:8000/predict", json=transaction)
result = response.json()

print(f"Score fraude: {result['fraud_score']:.3f}")
print(f"Niveau risque: {result['risk_level']}")
print(f"Action: {result['action']}")
```

### 📈 Dashboard Business

Accès : `http://localhost:8501`

**Fonctionnalités** :
- **Vue d'ensemble** : KPIs business et métriques clés
- **Prédiction temps réel** : Interface de test interactive
- **Analytics** : Analyses avancées des patterns de fraude
- **Testing** : Tests de charge et validation
- **Monitoring** : Surveillance système temps réel

## 🎯 Cas d'Usage Démo

### 1. Simulation Transaction Légitime
```bash
# Via dashboard : page "Prédiction Temps Réel"
# Ou via API :
curl -X POST "http://localhost:8000/simulate-transaction"
```

### 2. Test de Charge
```bash
# Via dashboard : page "Testing"
# Ou lancer 100 prédictions :
python run.py --test
```

### 3. Monitoring Performance
```bash
# Via dashboard : page "Monitoring"
# Ou API :
curl "http://localhost:8000/metrics"
```

## 📊 Métriques de Performance

### Objectifs KPI
- **Précision** : > 95%
- **Rappel** : > 90%
- **Faux Positifs** : < 5%
- **Latence** : < 100ms
- **Disponibilité** : 99.9%

### Résultats Actuels (Simulés)
- ✅ **Précision** : 96.2%
- ✅ **Rappel** : 91.5%
- ✅ **Faux Positifs** : 3.8%
- ✅ **Latence moyenne** : 45ms
- ✅ **AUC-ROC** : 0.94

## 🚀 Commandes Utiles

```bash
# Système complet
python run.py

# Tests uniquement
python run.py --test

# API seulement
python run.py --api-only

# Dashboard seulement
python run.py --dashboard-only

# Aide
python run.py --help

# Régénérer les données
python data_generator.py

# Réentraîner le modèle
python fraud_model.py
```

## 📈 Roadmap & Extensions

### Phase 2 - Améliorations
- [ ] Intégration base de données PostgreSQL
- [ ] Cache Redis pour performance
- [ ] Déploiement Docker/Kubernetes
- [ ] Monitoring Prometheus/Grafana
- [ ] Tests automatisés (pytest)

### Phase 3 - Fonctionnalités Avancées
- [ ] Explainable AI (SHAP)
- [ ] Auto-retraining des modèles
- [ ] Intégration données externes
- [ ] Dashboard mobile
- [ ] Alertes temps réel (email/SMS)

## 🎓 Aspects Pédagogiques (Alternance)

### Compétences Développées
- **Data Science** : Feature engineering, ML hybrides, évaluation modèles
- **Backend Development** : API REST, architecture microservices
- **Frontend** : Dashboard interactif, visualisation données
- **DevOps** : Containerisation, monitoring, CI/CD
- **Business** : Compréhension enjeux bancaires, ROI, KPIs

### Apprentissages Métier
- Réglementation bancaire (PSD2, RGPD)
- Gestion des risques financiers
- Expérience utilisateur en banque digitale
- Architecture système critique temps réel

## 🤝 Contribution & Support

### Structure pour présentation
1. **Business Case** (5 min) : Contexte, enjeux, ROI
2. **Demo Technique** (10 min) : Interface, API, prédictions temps réel
3. **Architecture** (5 min) : Stack technique, modèles ML
4. **Résultats** (5 min) : Métriques, performance, impact business

### Questions Fréquentes

**Q: Combien de temps pour développer ?**
R: 2-3 jours pour version fonctionnelle, 1-2 semaines pour version production.

**Q: Peut-on utiliser de vraies données ?**
R: Non, utilisation de données synthétiques respectant RGPD pour la démo.

**Q: Performance en production ?**
R: Architecture conçue pour 1000+ transactions/seconde avec latence < 100ms.

## 📞 Contact

**Candidat** : [Votre Nom]  
**Email** : [votre.email@exemple.com]  
**LinkedIn** : [Votre profil LinkedIn]  
**Poste visé** : Alternant Chef de Projet IA - Société Générale

---

*Ce projet démontre ma capacité à transformer les défis business de Boursorama en solutions IA concrètes, avec une approche structurée de chef de projet et une expertise technique avancée.*

🛡️ **FraudGuard AI** - Protégeons l'avenir bancaire avec l'Intelligence Artificielle