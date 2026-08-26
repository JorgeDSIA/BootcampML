"""API de inferencia (FastAPI) que sirve el modelo de rotación de empleados.

KServe usa /health y /ready para gestionar el ciclo de vida del pod; /predict
es el endpoint real que consume el frontend.
"""
from fastapi import FastAPI
from src.schemas import EmployeeFeatures, PredictionResponse
from src.predictor import Predictor

app = FastAPI(title="Attrition Prediction Service", version="1.0.0")
predictor = Predictor()  # el modelo se carga una sola vez, al iniciar el proceso


@app.get("/health")
def health():
    """Chequeo de salud básico (el proceso está vivo)."""
    return {"status": "ok"}


@app.get("/ready")
def ready():
    """Chequeo de disponibilidad: indica si el modelo ya terminó de cargar."""
    return {"status": "ready", "model_loaded": predictor.is_loaded()}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: EmployeeFeatures):
    """Recibe los datos del empleado, calcula features derivadas y devuelve la predicción."""
    result = predictor.predict(features.to_model_input())
    return result