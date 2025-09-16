"""
📊 Générateur de Données Synthétiques FraudGuard AI
Génère des transactions bancaires réalistes avec patterns de fraude
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from config import *

class TransactionGenerator:
    """Générateur de transactions bancaires synthétiques"""
    
    def __init__(self):
        # Catégories de marchands réalistes
        self.merchant_categories = [
            'grocery', 'restaurant', 'gas_station', 'retail', 'online',
            'pharmacy', 'entertainment', 'travel', 'telecom', 'insurance'
        ]
        
        # Types de devices
        self.device_types = ['mobile', 'desktop', 'tablet', 'atm']
        
        # Méthodes de paiement
        self.payment_methods = ['card_chip', 'card_swipe', 'contactless', 'online']
        
        # Patterns de fraude
        self.fraud_patterns = [
            'amount_spike',      # Montants anormalement élevés
            'velocity_attack',   # Transactions très rapides
            'geographic_anomaly', # Localisation inhabituelle
            'time_anomaly',      # Heures inhabituelles
            'merchant_anomaly'   # Catégories inhabituelles
        ]
    
    def generate_legitimate_transaction(self, user_id, transaction_id):
        """Génère une transaction légitime avec patterns réalistes"""
        
        # Patterns temporels réalistes
        hour = np.random.choice(range(24), p=self._get_hour_distribution())
        day_of_week = random.randint(0, 6)
        
        # Montants selon catégorie
        category = random.choice(self.merchant_categories)
        amount = self._get_realistic_amount(category)
        
        # Données utilisateur
        user_age = random.randint(18, 80)
        account_age_days = random.randint(30, 3650)  # 1 mois à 10 ans
        
        # Patterns comportementaux
        transaction_count_day = np.random.poisson(3)  # Moyenne 3 trans/jour
        amount_last_hour = random.uniform(0, 200)
        amount_last_day = random.uniform(50, 1000)
        
        # Métriques de vélocité
        velocity_1h = random.randint(0, 5)  # Max 5 transactions/heure
        avg_amount_30d = random.uniform(50, 500)
        std_amount_30d = random.uniform(20, 200)
        
        # Scores de risque (bas pour transactions légitimes)
        geographic_risk = random.uniform(0.0, 0.3)
        device_risk = random.uniform(0.0, 0.2)
        time_since_last_transaction = random.randint(10, 1440)  # minutes
        
        return {
            'transaction_id': transaction_id,
            'user_id': user_id,
            'timestamp': datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=hour,
                minutes=random.randint(0, 59)
            ),
            'amount': round(amount, 2),
            'merchant_category': category,
            'hour': hour,
            'day_of_week': day_of_week,
            'month': random.randint(1, 12),
            'user_age': user_age,
            'account_age_days': account_age_days,
            'transaction_count_day': transaction_count_day,
            'amount_last_hour': round(amount_last_hour, 2),
            'amount_last_day': round(amount_last_day, 2),
            'velocity_1h': velocity_1h,
            'avg_amount_30d': round(avg_amount_30d, 2),
            'std_amount_30d': round(std_amount_30d, 2),
            'geographic_risk': round(geographic_risk, 3),
            'device_risk': round(device_risk, 3),
            'device_type': random.choice(self.device_types),
            'payment_method': random.choice(self.payment_methods),
            'time_since_last_transaction': time_since_last_transaction,
            'is_fraud': 0  # Transaction légitime
        }
    
    def generate_fraud_transaction(self, user_id, transaction_id):
        """Génère une transaction frauduleuse avec patterns suspects"""
        
        # Choisir un pattern de fraude
        fraud_pattern = random.choice(self.fraud_patterns)
        
        # Base transaction légitime
        transaction = self.generate_legitimate_transaction(user_id, transaction_id)
        
        # Modifier selon le pattern de fraude
        if fraud_pattern == 'amount_spike':
            # Montants anormalement élevés
            transaction['amount'] = random.uniform(1000, 10000)
            transaction['geographic_risk'] = random.uniform(0.6, 1.0)
            
        elif fraud_pattern == 'velocity_attack':
            # Transactions très rapides
            transaction['velocity_1h'] = random.randint(8, 20)
            transaction['transaction_count_day'] = random.randint(15, 50)
            transaction['time_since_last_transaction'] = random.randint(1, 5)
            
        elif fraud_pattern == 'geographic_anomaly':
            # Localisation inhabituelle
            transaction['geographic_risk'] = random.uniform(0.7, 1.0)
            transaction['device_risk'] = random.uniform(0.5, 0.9)
            
        elif fraud_pattern == 'time_anomaly':
            # Heures très inhabituelles
            transaction['hour'] = random.choice([1, 2, 3, 4, 5])  # Nuit
            transaction['day_of_week'] = random.choice([0, 6])     # Week-end
            
        elif fraud_pattern == 'merchant_anomaly':
            # Catégories inhabituelles pour l'utilisateur
            transaction['merchant_category'] = 'online'
            transaction['amount'] = random.uniform(500, 5000)
            transaction['device_risk'] = random.uniform(0.6, 1.0)
        
        # Marquer comme fraude
        transaction['is_fraud'] = 1
        transaction['fraud_pattern'] = fraud_pattern
        
        return transaction
    
    def _get_hour_distribution(self):
        """Distribution réaliste des heures de transaction"""
        # Plus d'activité en journée
        probs = np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5h (nuit)
            0.03, 0.05, 0.08, 0.10, 0.12, 0.12,  # 6-11h (matin)
            0.10, 0.08, 0.06, 0.05, 0.04, 0.04,  # 12-17h (après-midi)
            0.06, 0.08, 0.06, 0.04, 0.02, 0.01   # 18-23h (soir)
        ])
        return probs / probs.sum()
    
    def _get_realistic_amount(self, category):
        """Montants réalistes selon la catégorie"""
        ranges = {
            'grocery': (10, 150),
            'restaurant': (15, 100),
            'gas_station': (20, 80),
            'retail': (25, 300),
            'online': (10, 500),
            'pharmacy': (5, 50),
            'entertainment': (20, 200),
            'travel': (100, 2000),
            'telecom': (30, 150),
            'insurance': (50, 500)
        }
        
        min_amt, max_amt = ranges.get(category, (10, 200))
        
        # Distribution log-normale pour montants réalistes
        return np.random.lognormal(
            mean=np.log((min_amt + max_amt) / 2),
            sigma=0.5
        )
    
    def generate_dataset(self, n_transactions=N_TRANSACTIONS, fraud_rate=FRAUD_RATE):
        """Génère un dataset complet de transactions"""
        print(f"🔄 Génération de {n_transactions} transactions (fraude: {fraud_rate*100:.1f}%)")
        
        transactions = []
        n_frauds = int(n_transactions * fraud_rate)
        n_legitimate = n_transactions - n_frauds
        
        # Générer transactions légitimes
        for i in range(n_legitimate):
            user_id = f"user_{random.randint(1000, 9999)}"
            transaction_id = f"txn_{i:06d}"
            transactions.append(
                self.generate_legitimate_transaction(user_id, transaction_id)
            )
        
        # Générer transactions frauduleuses
        for i in range(n_frauds):
            user_id = f"user_{random.randint(1000, 9999)}"
            transaction_id = f"txn_{n_legitimate + i:06d}"
            transactions.append(
                self.generate_fraud_transaction(user_id, transaction_id)
            )
        
        # Mélanger et convertir en DataFrame
        random.shuffle(transactions)
        df = pd.DataFrame(transactions)
        
        print(f"✅ Dataset généré:")
        print(f"   📊 Total: {len(df)} transactions")
        print(f"   ✅ Légitimes: {len(df[df['is_fraud']==0])} ({len(df[df['is_fraud']==0])/len(df)*100:.1f}%)")
        print(f"   🚨 Fraudes: {len(df[df['is_fraud']==1])} ({len(df[df['is_fraud']==1])/len(df)*100:.1f}%)")
        
        return df

def main():
    """Fonction principale - génère et sauvegarde les données"""
    print("🚀 Lancement du générateur de données FraudGuard AI")
    
    # Créer le générateur
    generator = TransactionGenerator()
    
    # Générer le dataset
    df = generator.generate_dataset()
    
    # Sauvegarder
    output_file = TRANSACTIONS_FILE
    df.to_csv(output_file, index=False)
    
    print(f"💾 Données sauvegardées: {output_file}")
    print(f"🔍 Aperçu des données:")
    print(df.head())
    print(f"\n📈 Statistiques:")
    print(df.describe())
    
    # Vérifier la qualité des données
    print(f"\n🔍 Vérifications qualité:")
    print(f"   Valeurs manquantes: {df.isnull().sum().sum()}")
    print(f"   Doublons: {df.duplicated().sum()}")
    print(f"   Montants négatifs: {(df['amount'] < 0).sum()}")
    
    print("\n✅ Génération de données terminée avec succès!")

if __name__ == "__main__":
    main()