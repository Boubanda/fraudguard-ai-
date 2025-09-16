"""
🌐 API FraudGuard AI - FastAPI Server
API temps réel pour détection de fraude bancaire
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time
import psutil
import asyncio
from datetime import datetime
import pandas as pd

from config import *
from fraud_model import FraudDetector

# ===== MODÈLES PYDANTIC =====

class TransactionRequest(BaseModel):
    """Modèle de requête pour une transaction"""
    transaction_id: str = Field(..., description="ID unique de la transaction")
    user_id: str = Field(..., description="ID de l'utilisateur")
    amount: float = Field(..., gt=0, description="Montant de la transaction")
    merchant_category: str = Field(..., description="Catégorie du marchand")
    hour: int = Field(..., ge=0, le=23, description="Heure de la transaction")
    day_of_week: int = Field(..., ge=0, le=6, description="Jour de la semaine (0=Lundi)")
    month: int = Field(..., ge=1, le=12, description="Mois")
    user_age: int = Field(..., gt=0, description="Âge de l'utilisateur")
    account_age_days: int = Field(..., gt=0, description="Âge du compte en jours")
    transaction_count_day: int = Field(..., ge=0, description="Nb transactions aujourd'hui")
    amount_last_hour: float = Field(..., ge=0, description="Montant dernière heure")
    amount_last_day: float = Field(..., ge=0, description="Montant dernier jour")
    velocity_1h: int = Field(..., ge=0, description="Nb transactions dernière heure")
    avg_amount_30d: float = Field(..., ge=0, description="Montant moyen 30 jours")
    std_amount_30d: float = Field(..., ge=0, description="Écart-type montant 30 jours")
    geographic_risk: float = Field(..., ge=0, le=1, description="Score risque géographique")
    device_risk: float = Field(..., ge=0, le=1, description="Score risque device")
    device_type: str = Field(..., description="Type de device")
    payment_method: str = Field(..., description="Méthode de paiement")
    time_since_last_transaction: int = Field(..., ge=0, description="Minutes depuis dernière transaction")

class PredictionResponse(BaseModel):
    """Modèle de réponse pour une prédiction"""
    transaction_id: str
    fraud_score: float = Field(..., description="Score de fraude (0-1)")
    xgb_score: float = Field(..., description="Score XGBoost")
    isolation_score: float = Field(..., description="Score Isolation Forest")
    risk_level: str = Field(..., description="Niveau de risque")
    action: str = Field(..., description="Action recommandée")
    is_fraud_predicted: bool = Field(..., description="Prédiction binaire")
    processing_time_ms: float = Field(..., description="Temps de traitement (ms)")
    timestamp: datetime = Field(..., description="Timestamp de la prédiction")

class BatchPredictionRequest(BaseModel):
    """Modèle pour prédictions en lot"""
    transactions: List[TransactionRequest]

class SystemMetrics(BaseModel):
    """Métriques système"""
    api_status: str
    model_loaded: bool
    total_predictions: int
    avg_processing_time_ms: float
    memory_usage_percent: float
    cpu_usage_percent: float
    uptime_seconds: float
    last_prediction_time: Optional[datetime]

class HealthResponse(BaseModel):
    """Réponse health check"""
    status: str
    timestamp: datetime
    version: str
    model_status: str

# ===== INITIALISATION API =====

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
fraud_detector = None
api_metrics = {
    "start_time": time.time(),
    "total_predictions": 0,
    "total_processing_time": 0.0,
    "last_prediction_time": None
}

# ===== STARTUP/SHUTDOWN =====

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    global fraud_detector
    
    print("🚀 Démarrage de l'API FraudGuard...")
    
    # Charger le modèle
    fraud_detector = FraudDetector()
    model_loaded = fraud_detector.load_model()
    
    if model_loaded:
        print("✅ Modèle chargé avec succès")
    else:
        print("⚠️ Aucun modèle trouvé - Mode entraînement requis")
    
    print(f"🌐 API démarrée sur http://localhost:{API_PORT}")
    print(f"📚 Documentation: http://localhost:{API_PORT}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    print("🛑 Arrêt de l'API FraudGuard")

# ===== ENDPOINTS PRINCIPAUX =====

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "🛡️ FraudGuard AI API",
        "version": API_VERSION,
        "status": "running",
        "endpoints": {
            "predict": "/predict",
            "batch": "/batch-predict",
            "metrics": "/metrics",
            "health": "/health",
            "docs": "/docs"
        },
        "documentation": f"http://localhost:{API_PORT}/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check de l'API"""
    model_status = "loaded" if fraud_detector and hasattr(fraud_detector, 'xgb_model') else "not_loaded"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=API_VERSION,
        model_status=model_status
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(transaction: TransactionRequest):
    """Prédiction de fraude pour une transaction"""
    
    if not fraud_detector:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    start_time = time.time()
    
    try:
        # Convertir en dict pour le modèle
        transaction_dict = transaction.dict()
        transaction_dict['timestamp'] = datetime.now()
        
        # Prédiction
        result = fraud_detector.predict(transaction_dict)
        
        # Calculer le temps de traitement
        processing_time = (time.time() - start_time) * 1000
        
        # Mettre à jour les métriques
        api_metrics["total_predictions"] += 1
        api_metrics["total_processing_time"] += processing_time
        api_metrics["last_prediction_time"] = datetime.now()
        
        # Construire la réponse
        response = PredictionResponse(
            transaction_id=transaction.transaction_id,
            fraud_score=result["fraud_score"],
            xgb_score=result["xgb_score"],
            isolation_score=result["isolation_score"],
            risk_level=result["risk_level"],
            action=result["action"],
            is_fraud_predicted=result["is_fraud_predicted"],
            processing_time_ms=processing_time,
            timestamp=datetime.now()
        )
        
        # Log pour monitoring
        print(f"🔍 Prédiction: {transaction.transaction_id} | Score: {result['fraud_score']:.3f} | Risque: {result['risk_level']} | {processing_time:.1f}ms")
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/batch-predict")
async def batch_predict(batch_request: BatchPredictionRequest):
    """Prédictions en lot"""
    
    if not fraud_detector:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    start_time = time.time()
    results = []
    
    try:
        for transaction in batch_request.transactions:
            transaction_dict = transaction.dict()
            transaction_dict['timestamp'] = datetime.now()
            
            result = fraud_detector.predict(transaction_dict)
            
            prediction_result = {
                "transaction_id": transaction.transaction_id,
                "fraud_score": result["fraud_score"],
                "risk_level": result["risk_level"],
                "action": result["action"],
                "is_fraud_predicted": result["is_fraud_predicted"]
            }
            results.append(prediction_result)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Mettre à jour métriques
        api_metrics["total_predictions"] += len(batch_request.transactions)
        api_metrics["total_processing_time"] += processing_time
        api_metrics["last_prediction_time"] = datetime.now()
        
        return {
            "predictions": results,
            "total_transactions": len(batch_request.transactions),
            "processing_time_ms": processing_time,
            "avg_time_per_transaction_ms": processing_time / len(batch_request.transactions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur batch: {str(e)}")

@app.get("/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Métriques système et performance"""
    
    # Métriques système
    memory_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent(interval=1)
    uptime = time.time() - api_metrics["start_time"]
    
    # Métriques API
    avg_processing_time = (
        api_metrics["total_processing_time"] / api_metrics["total_predictions"]
        if api_metrics["total_predictions"] > 0 else 0
    )
    
    return SystemMetrics(
        api_status="running",
        model_loaded=fraud_detector is not None,
        total_predictions=api_metrics["total_predictions"],
        avg_processing_time_ms=avg_processing_time,
        memory_usage_percent=memory_percent,
        cpu_usage_percent=cpu_percent,
        uptime_seconds=uptime,
        last_prediction_time=api_metrics["last_prediction_time"]
    )

@app.get("/model-info")
async def get_model_info():
    """Informations sur le modèle chargé"""
    
    if not fraud_detector:
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    
    return {
        "model_type": "Hybrid (XGBoost + Isolation Forest)",
        "features_count": len(FEATURES),
        "performance_metrics": fraud_detector.performance_metrics,
        "feature_importance": dict(sorted(
            fraud_detector.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]) if fraud_detector.feature_importance else {},
        "thresholds": {
            "high": FRAUD_THRESHOLD_HIGH,
            "medium": FRAUD_THRESHOLD_MEDIUM,
            "low": FRAUD_THRESHOLD_LOW
        }
    }

@app.post("/simulate-transaction")
async def simulate_transaction():
    """Simule une transaction aléatoire pour tests"""
    
    # Générer une transaction de test
    import random
    from datetime import datetime
    
    test_transaction = TransactionRequest(
        transaction_id=f"sim_{int(time.time())}",
        user_id=f"user_{random.randint(1000, 9999)}",
        amount=round(random.uniform(10, 1000), 2),
        merchant_category=random.choice(['grocery', 'restaurant', 'online', 'retail']),
        hour=random.randint(0, 23),
        day_of_week=random.randint(0, 6),
        month=random.randint(1, 12),
        user_age=random.randint(18, 80),
        account_age_days=random.randint(30, 3650),
        transaction_count_day=random.randint(0, 10),
        amount_last_hour=round(random.uniform(0, 200), 2),
        amount_last_day=round(random.uniform(50, 1000), 2),
        velocity_1h=random.randint(0, 5),
        avg_amount_30d=round(random.uniform(50, 500), 2),
        std_amount_30d=round(random.uniform(20, 200), 2),
        geographic_risk=round(random.uniform(0, 0.3), 3),
        device_risk=round(random.uniform(0, 0.2), 3),
        device_type=random.choice(['mobile', 'desktop', 'tablet']),
        payment_method=random.choice(['card_chip', 'contactless', 'online']),
        time_since_last_transaction=random.randint(10, 1440)
    )
    
    # Faire la prédiction
    prediction = await predict_fraud(test_transaction)
    
    return {
        "transaction": test_transaction.dict(),
        "prediction": prediction.dict()
    }

# ===== FONCTION DE LANCEMENT =====

def run_server():
    """Lance le serveur API"""
    import uvicorn
    
    print(f"🚀 Lancement du serveur FraudGuard AI")
    print(f"🌐 URL: http://{API_HOST}:{API_PORT}")
    print(f"📚 Documentation: http://{API_HOST}:{API_PORT}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_server()