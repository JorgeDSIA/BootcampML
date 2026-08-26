"""Frontend Flask: muestra el formulario y llama a la API de inferencia.

No contiene ninguna lógica del modelo — solo arma el payload y hace un POST
al servicio de inferencia (FastAPI/KServe) configurado en MODEL_ENDPOINT.
"""
import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# FastAPI inference endpoint
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT", "http://localhost:8080/predict")

app = Flask(__name__)
CORS(app)  # permite que el navegador llame a este backend desde otro origen


@app.route('/')
def index():
    """Sirve el formulario HTML principal."""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Recibe el formulario, arma el payload esperado por la API y reenvía la solicitud."""
    data = request.get_json(force=True)
    print('incoming-data: ', data)

    try:
        # Compute derived features
        yac = float(data["Years at Company"])
        ct  = float(data["Company Tenure"])
        jl  = int(data["Job Level"])

        payload = {
            "years_at_company":     yac,
            "performance_rating":   float(data["Performance Rating"]),
            "no_of_promotions":     int(data["Number of Promotions"]),
            "overtime":             int(data["Overtime"]),
            "edu_level":            int(data["Education Level"]),
            "no_of_dependents":     int(data["Number of Dependents"]),
            "job_level":            jl,
            "company_size":         int(data["Company Size"]),
            "company_tenure":       ct,
            "remote_work":          int(data["Remote Work"]),
            "company_reputation":   float(data["Company Reputation"]),
            "overall_satisfaction": float(data["OverallSatisfaction"]),
            "opportunities":        float(data["Opportunities"]),
            "annual_income":        int(data["AnnualIncome"]),
            "age_group":            int(data["AgeGroup"]),
        }

        resp = requests.post(MODEL_ENDPOINT, json=payload, timeout=10)
        resp.raise_for_status()

        # FastAPI returns the final shape — pass through directly
        return jsonify(resp.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)