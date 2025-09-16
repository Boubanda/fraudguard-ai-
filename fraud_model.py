"""
🤖 Modèle ML FraudGuard AI
Détection de fraude hybride: XGBoost + Isolation Forest
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

from config import *

class FraudDetector:
    """Détecteur de fraude hybride avec modèles multiples"""
    
    def __init__(self):
        # Modèles ML
        self.xgb_model = XGBClassifier(**XGBOOST_PARAMS)
        self.isolation_forest = IsolationForest(**ISOLATION_FOREST_PARAMS)
        
        # Preprocessing
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Métriques
        self.performance_metrics = {}
        self.feature_importance = {}
        
        print("🤖 FraudDetector initialisé")
    
    def preprocess_data(self, df):
        """Preprocessing des données pour ML"""
        print("🔄 Preprocessing des données...")
        
        # Copie pour éviter modifications
        data = df.copy()
        
        # Traitement des variables temporelles
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        data['is_night'] = data['hour'].isin([0, 1, 2, 3, 4, 5]).astype(int)
        
        # Feature engineering avancé
        data['amount_log'] = np.log1p(data['amount'])
        data['velocity_risk'] = data['velocity_1h'] / (data['avg_amount_30d'] + 1)
        data['amount_deviation'] = abs(data['amount'] - data['avg_amount_30d']) / (data['std_amount_30d'] + 1)
        data['total_risk_score'] = data['geographic_risk'] + data['device_risk']
        
        # Encodage des variables catégorielles
        for feature in CATEGORICAL_FEATURES:
            if feature in data.columns:
                if feature not in self.label_encoders:
                    self.label_encoders[feature] = LabelEncoder()
                    data[f'{feature}_encoded'] = self.label_encoders[feature].fit_transform(data[feature].astype(str))
                else:
                    data[f'{feature}_encoded'] = self.label_encoders[feature].transform(data[feature].astype(str))
        
        # Sélection des features finales
        feature_columns = [
            'amount', 'amount_log', 'hour', 'day_of_week', 'month',
            'user_age', 'account_age_days', 'transaction_count_day',
            'amount_last_hour', 'amount_last_day', 'velocity_1h',
            'avg_amount_30d', 'std_amount_30d', 'geographic_risk',
            'device_risk', 'time_since_last_transaction',
            'is_weekend', 'is_night', 'velocity_risk', 
            'amount_deviation', 'total_risk_score'
        ]
        
        # Ajouter les features encodées
        for feature in CATEGORICAL_FEATURES:
            encoded_col = f'{feature}_encoded'
            if encoded_col in data.columns:
                feature_columns.append(encoded_col)
        
        # Garder seulement les features existantes
        available_features = [col for col in feature_columns if col in data.columns]
        X = data[available_features]
        
        print(f"✅ Features utilisées: {len(available_features)}")
        print(f"   {available_features}")
        
        return X, data
    
    def train(self, df):
        """Entraînement des modèles hybrides"""
        print("🚀 Début de l'entraînement des modèles...")
        
        # Preprocessing
        X, processed_data = self.preprocess_data(df)
        y = df['is_fraud']
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"📊 Données d'entraînement:")
        print(f"   Train: {X_train.shape[0]} samples")
        print(f"   Test: {X_test.shape[0]} samples")
        print(f"   Features: {X_train.shape[1]}")
        print(f"   Fraudes train: {y_train.sum()} ({y_train.mean()*100:.1f}%)")
        
        # === ENTRAÎNEMENT ISOLATION FOREST ===
        print("\n🌲 Entraînement Isolation Forest...")
        self.isolation_forest.fit(X_train_scaled)
        
        # Prédictions anomalies
        isolation_train_pred = self.isolation_forest.decision_function(X_train_scaled)
        isolation_test_pred = self.isolation_forest.decision_function(X_test_scaled)
        
        # === HANDLING CLASS IMBALANCE AVEC SMOTE ===
        print("\n⚖️ Gestion du déséquilibre des classes...")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
        
        print(f"   Avant SMOTE: {y_train.value_counts().to_dict()}")
        print(f"   Après SMOTE: {pd.Series(y_train_balanced).value_counts().to_dict()}")
        
        # === ENTRAÎNEMENT XGBOOST ===
        print("\n🚀 Entraînement XGBoost...")
        self.xgb_model.fit(
            X_train_balanced, y_train_balanced,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False
        )
        
        # Importance des features
        self.feature_importance = dict(zip(X.columns, self.xgb_model.feature_importances_))
        
        # === ÉVALUATION ===
        print("\n📊 Évaluation des modèles...")
        self._evaluate_models(X_test_scaled, y_test, isolation_test_pred)
        
        print("✅ Entraînement terminé avec succès!")
        
        return self.performance_metrics
    
    def _evaluate_models(self, X_test, y_test, isolation_pred):
        """Évaluation complète des modèles"""
        
        # Prédictions XGBoost
        xgb_proba = self.xgb_model.predict_proba(X_test)[:, 1]
        xgb_pred = self.xgb_model.predict(X_test)
        
        # Prédictions Isolation Forest (convertir en probabilités)
        isolation_proba = (isolation_pred - isolation_pred.min()) / (isolation_pred.max() - isolation_pred.min())
        isolation_binary = (isolation_pred < 0).astype(int)
        
        # Prédictions hybrides (ensemble)
        hybrid_proba = (xgb_proba + (1 - isolation_proba)) / 2
        hybrid_pred = (hybrid_proba > 0.5).astype(int)
        
        # Métriques pour chaque modèle
        models_results = {
            'XGBoost': {
                'predictions': xgb_pred,
                'probabilities': xgb_proba
            },
            'Isolation Forest': {
                'predictions': isolation_binary,
                'probabilities': 1 - isolation_proba
            },
            'Hybrid Model': {
                'predictions': hybrid_pred,
                'probabilities': hybrid_proba
            }
        }
        
        print("\n🎯 RÉSULTATS DÉTAILLÉS:")
        print("=" * 50)
        
        for model_name, results in models_results.items():
            pred = results['predictions']
            proba = results['probabilities']
            
            # Métriques de base
            auc = roc_auc_score(y_test, proba)
            
            # Confusion matrix
            tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            
            print(f"\n📈 {model_name}:")
            print(f"   AUC: {auc:.3f}")
            print(f"   Precision: {precision:.3f}")
            print(f"   Recall: {recall:.3f}")
            print(f"   F1-Score: {f1:.3f}")
            print(f"   Specificity: {specificity:.3f}")
            print(f"   False Positive Rate: {fp/(fp+tn)*100:.1f}%")
            
            # Sauvegarder les métriques
            self.performance_metrics[model_name] = {
                'auc': auc,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'specificity': specificity,
                'false_positive_rate': fp/(fp+tn),
                'confusion_matrix': {'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn}
            }
        
        # Top features importantes
        print(f"\n🔍 TOP 10 FEATURES IMPORTANTES:")
        sorted_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:10]:
            print(f"   {feature}: {importance:.3f}")
    
    def predict(self, transaction_data):
        """Prédiction temps réel pour une transaction"""
        
        # Convertir en DataFrame si nécessaire
        if isinstance(transaction_data, dict):
            df = pd.DataFrame([transaction_data])
        else:
            df = transaction_data.copy()
        
        # Preprocessing
        X, _ = self.preprocess_data(df)
        X_scaled = self.scaler.transform(X)
        
        # Prédictions des deux modèles
        xgb_proba = self.xgb_model.predict_proba(X_scaled)[:, 1]
        isolation_score = self.isolation_forest.decision_function(X_scaled)
        
        # Normaliser isolation score
        isolation_proba = 1 / (1 + np.exp(-isolation_score))  # Sigmoid
        
        # Score hybride
        fraud_score = (xgb_proba + isolation_proba) / 2
        
        # Classification selon seuils
        if fraud_score[0] >= FRAUD_THRESHOLD_HIGH:
            risk_level = "HIGH"
            action = "BLOCK"
        elif fraud_score[0] >= FRAUD_THRESHOLD_MEDIUM:
            risk_level = "MEDIUM"
            action = "ALERT"
        elif fraud_score[0] >= FRAUD_THRESHOLD_LOW:
            risk_level = "LOW"
            action = "MONITOR"
        else:
            risk_level = "MINIMAL"
            action = "APPROVE"
        
        return {
            'fraud_score': float(fraud_score[0]),
            'xgb_score': float(xgb_proba[0]),
            'isolation_score': float(isolation_proba[0]),
            'risk_level': risk_level,
            'action': action,
            'is_fraud_predicted': fraud_score[0] > 0.5
        }
    
    def save_model(self, filepath=MODEL_PATH):
        """Sauvegarde du modèle complet"""
        model_data = {
            'xgb_model': self.xgb_model,
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'performance_metrics': self.performance_metrics,
            'feature_importance': self.feature_importance
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath=MODEL_PATH):
        """Chargement du modèle complet"""
        try:
            model_data = joblib.load(filepath)
            
            self.xgb_model = model_data['xgb_model']
            self.isolation_forest = model_data['isolation_forest']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.performance_metrics = model_data['performance_metrics']
            self.feature_importance = model_data['feature_importance']
            
            print(f"✅ Modèle chargé: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            return False

def main():
    """Fonction principale - entraînement du modèle"""
    print("🚀 Lancement de l'entraînement FraudGuard AI")
    
    # Charger les données
    print("📊 Chargement des données...")
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        print(f"✅ {len(df)} transactions chargées")
    except FileNotFoundError:
        print("❌ Fichier de données non trouvé. Lancez d'abord data_generator.py")
        return
    
    # Créer et entraîner le modèle
    detector = FraudDetector()
    metrics = detector.train(df)
    
    # Sauvegarder le modèle
    detector.save_model()
    
    # Test de prédiction
    print("\n🧪 Test de prédiction:")
    sample_transaction = df.iloc[0].to_dict()
    result = detector.predict(sample_transaction)
    print(f"   Transaction test: {result}")
    
    print("\n✅ Entraînement terminé avec succès!")
    print(f"📊 Modèle sauvegardé dans: {MODEL_PATH}")

if __name__ == "__main__":
    main()