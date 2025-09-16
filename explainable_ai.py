"""
🔍 Explainable AI pour FraudGuard - Version Intégrée
Intelligence Artificielle Explicable pour démonstration
"""

import pandas as pd
import numpy as np

class QuickExplainer:
    def __init__(self, fraud_detector):
        self.model = fraud_detector
    
    def explain_prediction(self, transaction_data, prediction_result):
        """Explication simple et efficace d'une prédiction"""
        
        factors = []
        
        # Analyser le montant
        amount = transaction_data.get('amount', 0)
        if amount > 1000:
            factors.append({
                'factor': 'Montant élevé',
                'value': f"{amount}€",
                'impact': 'RISK',
                'weight': 0.35,
                'explanation': 'Les transactions > 1000€ sont statistiquement plus risquées'
            })
        elif amount < 10:
            factors.append({
                'factor': 'Montant très faible',
                'value': f"{amount}€", 
                'impact': 'RISK',
                'weight': 0.25,
                'explanation': 'Les micro-transactions peuvent indiquer des tests de fraude'
            })
        
        # Analyser l'heure
        hour = transaction_data.get('hour', 12)
        if hour < 6 or hour > 22:
            factors.append({
                'factor': 'Heure inhabituelle',
                'value': f"{hour}h",
                'impact': 'RISK', 
                'weight': 0.3,
                'explanation': 'Transactions nocturnes plus susceptibles d\'être frauduleuses'
            })
        
        # Analyser le risque géographique
        geo_risk = transaction_data.get('geographic_risk', 0)
        if geo_risk > 0.5:
            factors.append({
                'factor': 'Localisation à risque',
                'value': f"{geo_risk:.0%}",
                'impact': 'RISK',
                'weight': 0.4,
                'explanation': 'Transaction depuis zone géographique non habituelle'
            })
        
        # Analyser la vélocité
        velocity = transaction_data.get('velocity_1h', 0)
        if velocity > 5:
            factors.append({
                'factor': 'Vélocité élevée', 
                'value': f"{velocity} trans/h",
                'impact': 'RISK',
                'weight': 0.35,
                'explanation': 'Trop de transactions en peu de temps'
            })
        
        # Si pas de facteurs de risque, ajouter facteurs positifs
        if not factors:
            factors.extend([
                {
                    'factor': 'Profil utilisateur normal',
                    'value': 'Comportement habituel',
                    'impact': 'SAFE',
                    'weight': 0.4,
                    'explanation': 'Transaction conforme au profil utilisateur'
                },
                {
                    'factor': 'Heure normale',
                    'value': f"{hour}h",
                    'impact': 'SAFE',
                    'weight': 0.3,
                    'explanation': 'Transaction durant heures normales d\'activité'
                }
            ])
        
        # Calcul score de confiance
        risk_factors = [f for f in factors if f['impact'] == 'RISK']
        confidence = prediction_result.get('fraud_score', 0.5)
        
        return {
            'factors': factors,
            'summary': f"Décision basée sur {len(factors)} indicateur(s) principal(aux)",
            'confidence': confidence,
            'risk_factors_count': len(risk_factors),
            'recommendation': self._generate_recommendation(factors, confidence)
        }
    
    def _generate_recommendation(self, factors, confidence):
        """Génère une recommandation basée sur l'analyse"""
        
        risk_factors = [f for f in factors if f['impact'] == 'RISK']
        
        if len(risk_factors) >= 3:
            return "🚨 BLOCAGE RECOMMANDÉ - Multiples indicateurs de risque détectés"
        elif len(risk_factors) == 2:
            return "⚠️ ALERTE - Investigation manuelle recommandée"  
        elif len(risk_factors) == 1:
            return "📊 SURVEILLANCE - Monitorer cette transaction"
        else:
            return "✅ APPROUVÉ - Profil de risque normal"

    def create_explanation_text(self, explanation):
        """Crée un texte d'explication formaté"""
        
        text = f"🧠 **EXPLICATION DE LA DÉCISION IA**\n\n"
        text += f"**Résumé:** {explanation['summary']}\n"
        text += f"**Confiance:** {explanation['confidence']:.1%}\n"
        text += f"**Recommandation:** {explanation['recommendation']}\n\n"
        
        text += "**📊 FACTEURS D'ANALYSE:**\n"
        for i, factor in enumerate(explanation['factors'], 1):
            emoji = "🚨" if factor['impact'] == 'RISK' else "✅"
            text += f"{i}. {emoji} **{factor['factor']}**: {factor['value']} "
            text += f"(Poids: {factor['weight']:.0%})\n"
            text += f"   💡 *{factor['explanation']}*\n\n"
        
        return text