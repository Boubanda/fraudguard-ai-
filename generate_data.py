"""
Générateur rapide de données pour FraudGuard AI
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_data():
    """Crée des données d'exemple"""
    
    np.random.seed(42)
    n_transactions = 5000
    
    # Générer des données basiques
    data = []
    
    for i in range(n_transactions):
        # Timestamp aléatoire dans les 30 derniers jours
        days_ago = np.random.randint(0, 30)
        hour = np.random.randint(0, 24)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hour)
        
        # Déterminer si c'est une fraude (2% de chance)
        is_fraud = np.random.random() < 0.02
        
        # Générer montant selon le profil
        if is_fraud:
            amount = np.random.choice([
                np.random.uniform(10, 50),    # Petits tests
                np.random.uniform(800, 2000)  # Gros montants
            ])
        else:
            amount = np.random.lognormal(4, 1)
            amount = max(5, min(amount, 1000))
        
        # Autres features
        transaction = {
            'transaction_id': f'txn_{i:06d}',
            'user_id': f'user_{np.random.randint(1000, 9999)}',
            'timestamp': timestamp,
            'amount': round(amount, 2),
            'merchant_category': np.random.choice(['grocery', 'restaurant', 'online', 'retail', 'gas_station']),
            'hour': hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            'user_age': np.random.randint(18, 75),
            'account_age_days': np.random.randint(30, 2000),
            'transaction_count_day': np.random.randint(1, 10),
            'amount_last_hour': np.random.uniform(0, 200),
            'amount_last_day': np.random.uniform(50, 1000),
            'velocity_1h': np.random.randint(1, 6),
            'avg_amount_30d': np.random.uniform(50, 500),
            'std_amount_30d': np.random.uniform(20, 200),
            'geographic_risk': np.random.uniform(0.0, 0.8) if not is_fraud else np.random.uniform(0.3, 1.0),
            'device_risk': np.random.uniform(0.0, 0.5) if not is_fraud else np.random.uniform(0.2, 1.0),
            'device_type': np.random.choice(['mobile', 'desktop', 'tablet']),
            'payment_method': np.random.choice(['card_chip', 'contactless', 'online', 'card_swipe']),
            'time_since_last_transaction': np.random.randint(5, 1440),
            'is_fraud': int(is_fraud)
        }
        data.append(transaction)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Génération des données...")
    
    # Créer les données
    df = create_sample_data()
    
    # Sauvegarder
    df.to_csv('data/transactions.csv', index=False)
    
    print(f"✅ {len(df)} transactions générées dans data/transactions.csv")
    print(f"🚨 {df['is_fraud'].sum()} fraudes ({df['is_fraud'].mean()*100:.1f}%)")
    print(f"💰 Montant total: {df['amount'].sum():,.0f}€")
    
    # Vérifier le fichier
    test_df = pd.read_csv('data/transactions.csv')
    print(f"✅ Vérification: fichier lisible avec {len(test_df)} lignes")
    print(f"📋 Colonnes: {', '.join(test_df.columns.tolist())}")