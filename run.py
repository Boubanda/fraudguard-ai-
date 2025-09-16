"""
🚀 Script de Lancement FraudGuard AI
Orchestration complète du système de détection de fraude
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

from config import *

class FraudGuardLauncher:
    """Lanceur principal du système FraudGuard AI"""
    
    def __init__(self):
        self.processes = {}
        self.running = False
        
    def check_dependencies(self):
        """Vérifie les dépendances et fichiers requis"""
        print("🔍 Vérification des dépendances...")
        
        # Vérifier les fichiers requis
        required_files = [
            'config.py',
            'data_generator.py', 
            'fraud_model.py',
            'api_server.py',
            'dashboard.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Fichiers manquants: {missing_files}")
            return False
        
        # Vérifier Python packages
        try:
            import pandas, numpy, sklearn, xgboost, fastapi, streamlit, plotly
            print("✅ Packages Python OK")
        except ImportError as e:
            print(f"❌ Package manquant: {e}")
            print("📦 Installez avec: pip install -r requirements.txt")
            return False
        
        print("✅ Toutes les dépendances sont installées")
        return True
    
    def setup_data(self):
        """Génère les données si nécessaire"""
        if not TRANSACTIONS_FILE.exists():
            print("📊 Génération des données synthétiques...")
            try:
                subprocess.run([sys.executable, "data_generator.py"], check=True)
                print("✅ Données générées avec succès")
            except subprocess.CalledProcessError:
                print("❌ Erreur lors de la génération des données")
                return False
        else:
            print("✅ Données déjà disponibles")
        return True
    
    def train_model(self):
        """Entraîne le modèle si nécessaire"""
        if not MODEL_PATH.exists():
            print("🤖 Entraînement du modèle ML...")
            try:
                subprocess.run([sys.executable, "fraud_model.py"], check=True)
                print("✅ Modèle entraîné avec succès")
            except subprocess.CalledProcessError:
                print("❌ Erreur lors de l'entraînement")
                return False
        else:
            print("✅ Modèle déjà disponible")
        return True
    
    def start_api_server(self):
        """Lance le serveur API"""
        print("🌐 Démarrage du serveur API...")
        
        try:
            process = subprocess.Popen([
                sys.executable, "api_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['api'] = process
            
            # Attendre que l'API soit prête
            time.sleep(3)
            
            if process.poll() is None:
                print(f"✅ API démarrée sur http://localhost:{API_PORT}")
                return True
            else:
                print("❌ Erreur démarrage API")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lancement API: {e}")
            return False
    
    def start_dashboard(self):
        """Lance le dashboard Streamlit"""
        print("📈 Démarrage du dashboard...")
        
        try:
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "dashboard.py",
                "--server.port", str(DASHBOARD_PORT),
                "--server.headless", "true"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['dashboard'] = process
            
            # Attendre que Streamlit soit prêt
            time.sleep(5)
            
            if process.poll() is None:
                print(f"✅ Dashboard démarré sur http://localhost:{DASHBOARD_PORT}")
                return True
            else:
                print("❌ Erreur démarrage dashboard")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lancement dashboard: {e}")
            return False
    
    def start_full_system(self):
        """Lance le système complet"""
        print("🚀 LANCEMENT FRAUDGUARD AI - SYSTÈME COMPLET")
        print("=" * 50)
        
        # Vérifications préliminaires
        if not self.check_dependencies():
            return False
        
        if not self.setup_data():
            return False
        
        if not self.train_model():
            return False
        
        # Démarrage des services
        print("\n🎯 Démarrage des services...")
        
        # API Server
        if not self.start_api_server():
            return False
        
        # Dashboard
        if not self.start_dashboard():
            return False
        
        self.running = True
        
        print("\n🎉 SYSTÈME FRAUDGUARD AI DÉMARRÉ AVEC SUCCÈS!")
        print("=" * 50)
        print(f"🌐 API Documentation: http://localhost:{API_PORT}/docs")
        print(f"📈 Dashboard Business: http://localhost:{DASHBOARD_PORT}")
        print(f"🔍 Health Check: http://localhost:{API_PORT}/health")
        print("=" * 50)
        print("💡 Commandes utiles:")
        print("   - Ctrl+C pour arrêter")
        print("   - python run.py --api-only (API seulement)")
        print("   - python run.py --dashboard-only (Dashboard seulement)")
        print("   - python run.py --test (Tests système)")
        
        return True
    
    def run_tests(self):
        """Exécute les tests du système"""
        print("🧪 TESTS DU SYSTÈME FRAUDGUARD AI")
        print("=" * 40)
        
        # Test 1: Génération de données
        print("\n📊 Test 1: Génération de données")
        if self.setup_data():
            print("✅ Test données: SUCCÈS")
        else:
            print("❌ Test données: ÉCHEC")
            return
        
        # Test 2: Entraînement modèle
        print("\n🤖 Test 2: Entraînement modèle")
        if self.train_model():
            print("✅ Test modèle: SUCCÈS")
        else:
            print("❌ Test modèle: ÉCHEC")
            return
        
        # Test 3: API
        print("\n🌐 Test 3: API Server")
        if self.start_api_server():
            print("✅ Test API: SUCCÈS")
            time.sleep(2)
            self.stop_process('api')
        else:
            print("❌ Test API: ÉCHEC")
            return
        
        # Test 4: Dashboard
        print("\n📈 Test 4: Dashboard")
        if self.start_dashboard():
            print("✅ Test Dashboard: SUCCÈS")
            time.sleep(3)
            self.stop_process('dashboard')
        else:
            print("❌ Test Dashboard: ÉCHEC")
            return
        
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ Le système FraudGuard AI est prêt à être déployé")
    
    def stop_process(self, service_name):
        """Arrête un processus spécifique"""
        if service_name in self.processes:
            process = self.processes[service_name]
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.processes[service_name]
            print(f"🛑 Service {service_name} arrêté")
    
    def stop_all(self):
        """Arrête tous les processus"""
        print("\n🛑 Arrêt du système FraudGuard AI...")
        
        for service_name in list(self.processes.keys()):
            self.stop_process(service_name)
        
        self.running = False
        print("✅ Système arrêté proprement")
    
    def monitor_processes(self):
        """Surveille les processus et redémarre si nécessaire"""
        while self.running:
            time.sleep(10)
            
            for service_name, process in list(self.processes.items()):
                if process.poll() is not None:
                    print(f"⚠️ Service {service_name} arrêté inattenduement")
                    
                    # Tentative de redémarrage
                    if service_name == 'api':
                        print("🔄 Redémarrage API...")
                        self.start_api_server()
                    elif service_name == 'dashboard':
                        print("🔄 Redémarrage Dashboard...")
                        self.start_dashboard()

def signal_handler(sig, frame):
    """Gestionnaire de signal pour arrêt propre"""
    global launcher
    print("\n🛑 Signal d'arrêt reçu...")
    launcher.stop_all()
    sys.exit(0)

def main():
    """Fonction principale avec gestion des arguments"""
    global launcher
    
    # Gestionnaire de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    launcher = FraudGuardLauncher()
    
    # Gestion des arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--test":
            launcher.run_tests()
            return
        
        elif arg == "--api-only":
            print("🌐 Lancement API seulement...")
            if launcher.check_dependencies() and launcher.setup_data() and launcher.train_model():
                if launcher.start_api_server():
                    print("✅ API démarrée. Appuyez sur Ctrl+C pour arrêter.")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        launcher.stop_all()
            return
        
        elif arg == "--dashboard-only":
            print("📈 Lancement Dashboard seulement...")
            if launcher.check_dependencies() and launcher.setup_data():
                if launcher.start_dashboard():
                    print("✅ Dashboard démarré. Appuyez sur Ctrl+C pour arrêter.")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        launcher.stop_all()
            return
        
        elif arg == "--help":
            print("🛡️ FRAUDGUARD AI - OPTIONS DE LANCEMENT")
            print("=" * 40)
            print("python run.py                 # Système complet")
            print("python run.py --test          # Tests système")
            print("python run.py --api-only      # API seulement")
            print("python run.py --dashboard-only # Dashboard seulement")
            print("python run.py --help          # Aide")
            return
    
    # Lancement système complet par défaut
    if launcher.start_full_system():
        # Démarrer le monitoring en arrière-plan
        monitor_thread = threading.Thread(target=launcher.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Maintenir le processus principal actif
            while launcher.running:
                time.sleep(1)
        except KeyboardInterrupt:
            launcher.stop_all()

if __name__ == "__main__":
    main()