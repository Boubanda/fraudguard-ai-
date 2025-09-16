"""
📊 Business Intelligence pour FraudGuard AI
Génération de métriques et rapports business automatiques
"""

from datetime import datetime, timedelta
import random
import json
import pandas as pd

class BusinessIntelligence:
    def __init__(self):
        self.company = "Société Générale"
        self.system_name = "FraudGuard AI"
        
    def generate_executive_summary(self, period_days=30):
        """Génère un résumé exécutif avec données simulées réalistes"""
        
        # Simulation de données business réalistes pour la démo
        base_transactions = random.randint(45000, 55000)
        fraud_rate = random.uniform(1.8, 2.5)
        fraud_count = int(base_transactions * fraud_rate / 100)
        
        # Calculs économiques
        avg_fraud_amount = random.uniform(150, 800)
        prevented_frauds = random.randint(800, 1200)  # Fraudes évitées grâce au système
        savings = prevented_frauds * avg_fraud_amount
        
        summary = {
            'period': f'{period_days} derniers jours',
            'generated_at': datetime.now().isoformat(),
            'metrics': {
                'total_transactions': base_transactions,
                'fraud_detected': fraud_count,
                'fraud_rate_percent': round(fraud_rate, 2),
                'model_accuracy': round(random.uniform(93, 96), 1),
                'false_positive_rate': round(random.uniform(2.1, 4.2), 1),
                'processing_time_avg_ms': round(random.uniform(35, 65), 1),
                'system_uptime': round(random.uniform(98.5, 99.9), 2)
            },
            'financial_impact': {
                'estimated_savings_period': int(savings),
                'estimated_savings_annual': int(savings * (365/period_days)),
                'roi_percent': round(random.uniform(280, 450), 0),
                'cost_per_transaction': round(random.uniform(0.02, 0.08), 3),
                'frauds_prevented': prevented_frauds
            },
            'executive_highlights': self._generate_executive_highlights(base_transactions, fraud_count, savings)
        }
        
        # Recommandations intelligentes
        recommendations = []
        
        if summary['metrics']['fraud_rate_percent'] > 2.2:
            recommendations.append("⚠️ Taux de fraude élevé - Réviser seuils de détection")
        
        if summary['metrics']['false_positive_rate'] > 3.5:
            recommendations.append("📊 Optimiser pour réduire faux positifs < 3%")
        
        if summary['metrics']['model_accuracy'] > 95:
            recommendations.append("✅ Excellente performance - Documenter bonnes pratiques")
        
        if summary['financial_impact']['estimated_savings_annual'] > 2000000:
            recommendations.append("💰 Objectif ROI dépassé - Considérer extension périmètre")
        
        recommendations.extend([
            "🚀 Étendre aux paiements internationaux (+30% couverture)",
            "📈 Intégrer données comportementales pour +5% précision",
            "🔄 Automatiser feedback équipes fraude",
            f"📊 Projection annuelle: {summary['financial_impact']['estimated_savings_annual']:,}€ d'économies"
        ])
        
        summary['recommendations'] = recommendations
        
        return summary
    
    def _generate_executive_highlights(self, transactions, fraud_count, savings):
        """Génère les points saillants pour la direction"""
        highlights = []
        
        if savings > 500000:
            highlights.append(f"💎 Économies estimées: {savings:,.0f}€")
        
        accuracy = random.uniform(93, 96)
        if accuracy > 94:
            highlights.append(f"🎯 Précision modèle: {accuracy:.1f}%")
            
        automation_rate = random.uniform(85, 95)
        if automation_rate > 90:
            highlights.append(f"🤖 Automatisation: {automation_rate:.1f}%")
            
        highlights.append("✅ Conformité RGPD assurée")
        
        return highlights
    
    def create_trend_data(self, months=12):
        """Crée des données de tendance pour graphiques"""
        
        # Noms de mois sur 12 mois (du plus ancien au plus récent)
        month_names = []
        base_date = datetime.now()
        for i in range(months-1, -1, -1):  # Inverser pour avoir chronologique
            month_date = base_date - timedelta(days=30*i)
            month_names.append(month_date.strftime("%b %Y"))
        
        # Simulation d'amélioration progressive
        base_fraud_rate = 3.2
        base_savings = 150000
        
        trends = {
            'months': month_names,
            'fraud_rates': [],
            'savings': []
        }
        
        for i in range(months):
            # Amélioration progressive des métriques (plus réaliste)
            fraud_rate = round(base_fraud_rate * (0.95 ** i) + random.uniform(-0.1, 0.1), 2)
            fraud_rate = max(1.5, fraud_rate)  # Pas en dessous de 1.5%
            
            monthly_savings = int(base_savings + (i * 15000) + random.randint(-10000, 20000))
            monthly_savings = max(100000, monthly_savings)  # Minimum 100k
            
            trends['fraud_rates'].append(fraud_rate)
            trends['savings'].append(monthly_savings)
        
        return trends
    
    def generate_compliance_report(self):
        """Génère un rapport de conformité réglementaire"""
        
        return {
            'gdpr_compliance': {
                'status': 'COMPLIANT',
                'score': random.randint(95, 99),
                'explainable_ai': True,
                'data_anonymization': True,
                'audit_trail': True,
                'right_to_explanation': True,
                'details': {
                    'data_protection': 'COMPLIANT',
                    'right_to_explanation': 'COMPLIANT',
                    'data_minimization': 'COMPLIANT',
                    'consent_management': 'COMPLIANT'
                }
            },
            'psd2_compliance': {
                'status': 'COMPLIANT',
                'score': random.randint(93, 98),
                'strong_authentication': True,
                'transaction_monitoring': True,
                'fraud_prevention': True,
                'details': {
                    'transaction_monitoring': 'COMPLIANT',
                    'fraud_prevention': 'COMPLIANT',
                    'reporting_requirements': 'COMPLIANT'
                }
            },
            'acpr_guidelines': {
                'status': 'COMPLIANT',
                'score': random.randint(90, 97),
                'ai_governance': True,
                'model_validation': True,
                'risk_management': True,
                'details': {
                    'ai_governance': 'COMPLIANT',
                    'model_validation': 'COMPLIANT',
                    'risk_management': 'COMPLIANT',
                    'operational_resilience': random.choice(['COMPLIANT', 'UNDER_REVIEW'])
                }
            },
            'overall_compliance_score': random.randint(94, 98),
            'risk_level': 'LOW',
            'last_audit_date': (datetime.now() - timedelta(days=45)).isoformat(),
            'next_audit_date': (datetime.now() + timedelta(days=90)).isoformat(),
            'action_items': [
                "Mettre à jour documentation processus IA",
                "Planifier audit trimestriel",
                "Réviser politique de rétention données"
            ]
        }
    
    def export_report(self, summary, format='json'):
        """Exporte le rapport dans différents formats"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            if format.lower() == 'json':
                filename = f'fraudguard_report_{timestamp}.json'
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
                return filename
            
            elif format.lower() == 'txt':
                filename = f'fraudguard_report_{timestamp}.txt'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"🛡️ {self.system_name} - Rapport Exécutif\n")
                    f.write(f"{self.company}\n")
                    f.write("="*60 + "\n\n")
                    
                    f.write(f"Période: {summary.get('period', 'N/A')}\n")
                    f.write(f"Généré le: {summary.get('generated_at', datetime.now().isoformat())}\n\n")
                    
                    # Métriques
                    if 'metrics' in summary:
                        f.write("📊 MÉTRIQUES PRINCIPALES:\n")
                        for key, value in summary['metrics'].items():
                            f.write(f"  • {key}: {value}\n")
                        f.write("\n")
                    
                    # Impact financier
                    if 'financial_impact' in summary:
                        f.write("💰 IMPACT FINANCIER:\n")
                        for key, value in summary['financial_impact'].items():
                            f.write(f"  • {key}: {value}\n")
                        f.write("\n")
                    
                    # Recommandations
                    if 'recommendations' in summary:
                        f.write("💡 RECOMMANDATIONS:\n")
                        for rec in summary['recommendations']:
                            f.write(f"  • {rec}\n")
                    
                    f.write(f"\n{'-'*60}\n")
                    f.write(f"Généré par {self.system_name} le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
                
                return filename
            
            else:
                raise ValueError(f"Format non supporté: {format}")
                
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return f"Erreur: {str(e)}"
    
    def get_kpi_summary(self, period_days=30):
        """Retourne un résumé des KPIs principaux"""
        
        summary = self.generate_executive_summary(period_days)
        
        return {
            'transactions_count': summary['metrics']['total_transactions'],
            'fraud_rate': summary['metrics']['fraud_rate_percent'],
            'model_accuracy': summary['metrics']['model_accuracy'],
            'annual_savings': summary['financial_impact']['estimated_savings_annual'],
            'roi': summary['financial_impact']['roi_percent'],
            'status': 'HEALTHY' if summary['metrics']['fraud_rate_percent'] < 2.5 else 'WARNING'
        }
    
    def compare_with_industry_benchmarks(self):
        """Compare les performances avec les benchmarks industrie"""
        
        # Benchmarks industrie typiques
        industry_benchmarks = {
            'fraud_rate': 2.7,
            'precision': 75.0,
            'processing_time_ms': 1500,
            'false_positive_rate': 8.0
        }
        
        # Nos performances simulées
        our_performance = {
            'fraud_rate': random.uniform(1.8, 2.3),
            'precision': random.uniform(93, 96),
            'processing_time_ms': random.uniform(40, 70),
            'false_positive_rate': random.uniform(2, 4)
        }
        
        comparison = {}
        for metric in industry_benchmarks:
            industry_val = industry_benchmarks[metric]
            our_val = our_performance[metric]
            
            # Calculer l'amélioration (pour fraude_rate et false_positive_rate, moins c'est mieux)
            if metric in ['fraud_rate', 'false_positive_rate', 'processing_time_ms']:
                improvement = ((industry_val - our_val) / industry_val) * 100
            else:
                improvement = ((our_val - industry_val) / industry_val) * 100
            
            comparison[metric] = {
                'industry_benchmark': industry_val,
                'our_performance': our_val,
                'improvement_percent': round(improvement, 1),
                'status': 'BETTER' if improvement > 0 else 'WORSE'
            }
        
        return comparison