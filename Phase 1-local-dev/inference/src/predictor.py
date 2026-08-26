"""Carga el modelo entrenado (model.pkl) y expone un método predict() para la API.

El orden de FEATURE_ORDER debe coincidir exactamente con el orden de columnas
usado durante el entrenamiento (ver src/model_training/01_training.py) — un
desorden aquí no genera error, solo predicciones incorrectas de forma silenciosa.
"""
import joblib
from pathlib import Path

FEATURE_ORDER = [
    "Years at Company", "Performance Rating", "Number of Promotions",
    "Overtime", "Education Level", "Number of Dependents",
    "Job Level", "Company Size", "Company Tenure", "Remote Work",
    "Company Reputation", "OverallSatisfaction", "Opportunities",
    "AnnualIncome", "AgeGroup", "RoleStagnationRatio", "TenureGap",
    "EarlyCompanyTenureRisk", "LongTenureLowRoleRisk"
]

THRESHOLD = 0.50  # a partir de que probabilidad se predice "se ira" (1)


class Predictor:
    """Envuelve el modelo cargado y traduce sus probabilidades a una respuesta de API."""

    def __init__(self):
        model_path = Path(__file__).resolve().parent.parent / "artifacts" / "model.pkl"
        try:
            obj = joblib.load(model_path)
            self.predict_fn = obj.predict  # bound method — not the full sklearn object
        except FileNotFoundError:
            raise RuntimeError(
                f"Model artifact not found at {model_path}. "
                "Train the model first (src/model_training) and copy artifacts/model.pkl here."
            )
        except AttributeError:
            raise RuntimeError(f"Loaded object at {model_path} has no 'predict' method.")

    def is_loaded(self) -> bool:
        """True si el modelo se cargó correctamente al iniciar el servicio."""
        return self.predict_fn is not None

    def predict(self, features: dict) -> dict:
        """Arma el vector de features en FEATURE_ORDER y devuelve la predicción final."""
        values  = [[features[k] for k in FEATURE_ORDER]]  # una sola fila, en el orden esperado por el modelo
        probs   = self.predict_fn(values)[0]  # [p_stay, p_leave]
        p_stay  = float(probs[0])
        p_leave = float(probs[1])

        return {
            "prediction": int(p_leave >= THRESHOLD),
            "p_leave":    round(p_leave, 4),
            "p_stay":     round(p_stay, 4),
            "risk":       self._tier(p_leave),
            "threshold":  THRESHOLD,
        }

    def _tier(self, prob: float) -> str:
        """Traduce la probabilidad de renuncia en un nivel de riesgo legible."""
        if prob >= 0.65: return "HIGH"
        if prob >= 0.45: return "MEDIUM"
        if prob >= 0.25: return "LOW"
        return "VERY_LOW"