"""
📊 Monitoring Système Simple pour FraudGuard AI
Surveillance temps réel des performances et métriques
"""

import psutil
import time
from datetime import datetime
from collections import deque
import threading

class SystemMonitor:
    def __init__(self):
        self.metrics_history = deque(maxlen=100)  # Garder 100 dernières mesures
        self.api_stats = {
            'total_requests': 0,
            'total_predictions': 0,
            'fraud_detected': 0,
            'errors': 0,
            'avg_response_time': 0.0,
            'uptime_start': datetime.now()
        }
        self.alerts = []
        
    def collect_system_metrics(self):
        """Collecte les métriques système actuelles"""
        
        # Métriques système réelles
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Métriques réseau simulées (en production: vraies métriques)
        import random
        network_io = random.uniform(10, 100)  # MB/s simulé
        active_connections = random.randint(15, 45)
        
        metrics = {
            'timestamp': datetime.now(),
            'cpu_usage_percent': round(cpu_percent, 1),
            'memory_usage_percent': round(memory.percent, 1),
            'disk_usage_percent': round(disk.percent, 1),
            'memory_available_gb': round(memory.available / (1024**3), 1),
            'network_io_mbps': round(network_io, 1),
            'active_connections': active_connections,
            'response_time_ms': round(random.uniform(25, 95), 1),
            'cache_hit_rate': round(random.uniform(0.75, 0.95), 3)
        }
        
        # Stocker dans l'historique
        self.metrics_history.append(metrics)
        
        return metrics
    
    def update_api_stats(self, prediction_result=None, response_time_ms=0, error=False):
        """Met à jour les statistiques API"""
        
        self.api_stats['total_requests'] += 1
        
        if prediction_result:
            self.api_stats['total_predictions'] += 1
            
            if prediction_result.get('is_fraud_predicted', False):
                self.api_stats['fraud_detected'] += 1
        
        if error:
            self.api_stats['errors'] += 1
        
        # Moyenne mobile du temps de réponse
        if response_time_ms > 0:
            current_avg = self.api_stats['avg_response_time']
            self.api_stats['avg_response_time'] = (current_avg * 0.9) + (response_time_ms * 0.1)
    
    def check_alerts(self):
        """Vérifie et génère les alertes selon les seuils"""
        
        current_metrics = self.collect_system_metrics()
        new_alerts = []
        
        # Seuils d'alerte
        if current_metrics['cpu_usage_percent'] > 85:
            new_alerts.append({
                'type': 'HIGH_CPU',
                'severity': 'WARNING' if current_metrics['cpu_usage_percent'] < 95 else 'CRITICAL',
                'message': f"CPU usage: {current_metrics['cpu_usage_percent']}%",
                'timestamp': datetime.now(),
                'value': current_metrics['cpu_usage_percent']
            })
        
        if current_metrics['memory_usage_percent'] > 90:
            new_alerts.append({
                'type': 'HIGH_MEMORY',
                'severity': 'CRITICAL',
                'message': f"Memory usage: {current_metrics['memory_usage_percent']}%",
                'timestamp': datetime.now(),
                'value': current_metrics['memory_usage_percent']
            })
        
        if current_metrics['response_time_ms'] > 150:
            new_alerts.append({
                'type': 'HIGH_LATENCY',
                'severity': 'WARNING',
                'message': f"Response time: {current_metrics['response_time_ms']:.0f}ms",
                'timestamp': datetime.now(),
                'value': current_metrics['response_time_ms']
            })
        
        # Ajouter nouvelles alertes
        self.alerts.extend(new_alerts)
        
        # Garder seulement les 20 dernières alertes
        if len(self.alerts) > 20:
            self.alerts = self.alerts[-20:]
        
        return new_alerts
    
    def get_dashboard_data(self):
        """Retourne toutes les données pour le dashboard"""
        
        current_metrics = self.collect_system_metrics()
        recent_alerts = self.check_alerts()
        
        # Calculs dérivés
        uptime_seconds = (datetime.now() - self.api_stats['uptime_start']).total_seconds()
        
        fraud_rate = 0
        if self.api_stats['total_predictions'] > 0:
            fraud_rate = (self.api_stats['fraud_detected'] / self.api_stats['total_predictions']) * 100
        
        error_rate = 0
        if self.api_stats['total_requests'] > 0:
            error_rate = (self.api_stats['errors'] / self.api_stats['total_requests']) * 100
        
        # Déterminer santé système
        system_health = 'HEALTHY'
        if len([a for a in self.alerts if a['severity'] == 'CRITICAL']) > 0:
            system_health = 'CRITICAL'
        elif len([a for a in self.alerts if a['severity'] == 'WARNING']) > 0:
            system_health = 'WARNING'
        
        return {
            'current_metrics': current_metrics,
            'api_statistics': {
                **self.api_stats,
                'uptime_hours': round(uptime_seconds / 3600, 1),
                'fraud_rate_percent': round(fraud_rate, 2),
                'error_rate_percent': round(error_rate, 2)
            },
            'alerts': self.alerts[-5:],  # 5 dernières alertes
            'system_health': system_health,
            'performance_trends': self._get_performance_trends()
        }
    
    def _get_performance_trends(self):
        """Calcule les tendances de performance"""
        
        if len(self.metrics_history) < 10:
            return {}
        
        # Dernières 10 mesures pour tendance
        recent_metrics = list(self.metrics_history)[-10:]
        
        cpu_values = [m['cpu_usage_percent'] for m in recent_metrics]
        memory_values = [m['memory_usage_percent'] for m in recent_metrics]
        response_values = [m['response_time_ms'] for m in recent_metrics]
        
        return {
            'cpu_trend': 'UP' if cpu_values[-1] > cpu_values[0] else 'DOWN',
            'memory_trend': 'UP' if memory_values[-1] > memory_values[0] else 'DOWN',
            'response_time_trend': 'UP' if response_values[-1] > response_values[0] else 'DOWN',
            'cpu_avg': round(sum(cpu_values) / len(cpu_values), 1),
            'memory_avg': round(sum(memory_values) / len(memory_values), 1),
            'response_avg': round(sum(response_values) / len(response_values), 1)
        }
    
    def start_background_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        
        def monitor_loop():
            while True:
                try:
                    self.collect_system_metrics()
                    self.check_alerts()
                    time.sleep(30)  # Collecte toutes les 30 secondes
                except Exception as e:
                    print(f"Erreur monitoring: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread

# Instance globale pour utilisation dans l'application
system_monitor = SystemMonitor()