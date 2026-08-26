# Fase 1: Desarrollo Local y Pipelines de Datos

Guía práctica para ejecutar, de punta a punta, el flujo local de este proyecto: preparación de datos → entrenamiento → API de inferencia → frontend → despliegue en Kubernetes.

> Caso de uso: predicción de rotación (attrition) de empleados.

## 0. Requisitos previos

- Python 3.11+ (probado con 3.12)
- Docker
- `kubectl` + un clúster con KServe instalado (solo para el paso de despliegue en K8s)

> Lista completa de requisitos técnicos del bootcamp (hardware, software, cuentas): ver [Requisitos Técnicos](../README.md#requisitos-t%C3%A9cnicos) en el README principal.

## 1. Preparar el entorno

**Linux / Mac:**

```bash
cd 02-phase-1-local-dev-mlops
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
cd 02-phase-1-local-dev-mlops
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Pipeline de preparación de datos

Los scripts importan con `from config.paths import ...`, así que `src/` debe estar en el `PYTHONPATH` (los nombres empiezan con dígitos, por lo que **no** se pueden ejecutar con `python -m`). Configura una sola vez por sesión de terminal:

**Linux / Mac:**

```bash
export PYTHONPATH="$PWD/src"
```

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH = "$PWD\src"
```

Luego ejecutar **en este orden** desde `02-phase-1-local-dev-mlops/` (los mismos comandos `python` funcionan igual en Windows y Linux/Mac). Cada script lee la salida del anterior (rutas definidas en `src/config/paths.py`) y escribe en `datasets/processed/`.

```bash
python src/data_preparation/01_ingestion.py
python src/data_preparation/02_validation.py
python src/data_preparation/03_eda.py
python src/data_preparation/04_cleaning.py
python src/data_preparation/05_feature_engg.py
python src/data_preparation/06_preprocessing.py
```

| Script | Entrada | Salida |
|---|---|---|
| `01_ingestion.py` | `datasets/employee_attrition.csv` | `datasets/processed/raw_ingested.csv` |
| `02_validation.py` | `raw_ingested.csv` | `validated.csv` (valida esquema con Pandera) |
| `03_eda.py` | `validated.csv` | `eda.csv` |
| `04_cleaning.py` | `eda.csv` | `cleaned.csv` |
| `05_feature_engg.py` | `cleaned.csv` | `featured.csv` (encoding, features derivadas) |
| `06_preprocessing.py` | `featured.csv` | `train.csv` / `test.csv` (split 80/20) |

## 3. Entrenamiento del modelo

Con `PYTHONPATH` ya configurado (paso 2):

```bash
python src/model_training/01_training.py
python src/model_training/02_evaluation.py
python src/model_training/03_cross_validation.py
python src/model_training/04_tuning.py
```

Esto genera `artifacts/model.pkl` (pipeline sklearn: `StandardScaler` + `LogisticRegression`) y `artifacts/metrics.json`.

Para probar el modelo entrenado localmente con datos de ejemplo:

```bash
python src/model_testing/predict.py
```

Para entender **por qué** el modelo predice lo que predice (explicabilidad con SHAP), sobre una predicción puntual y a nivel global del dataset:

```bash
python src/model_testing/explain.py
```

Usa `artifacts/pipeline.pkl` (el pipeline "crudo" que guarda `04_tuning.py`, distinto del `model.pkl` envuelto para inferencia) y genera `artifacts/shap_summary.png` con el ranking de features más influyentes.

## 4. Servir el modelo como API (FastAPI)

El servicio de inferencia espera el artefacto en `inference/artifacts/model.pkl`. Cópialo ahí después de entrenar:

**Linux / Mac:**

```bash
cp artifacts/model.pkl inference/artifacts/model.pkl
```

**Windows (PowerShell):**

```powershell
cp artifacts\model.pkl inference\artifacts\model.pkl
```

Ejecutar localmente sin Docker (mismos comandos en Windows y Linux/Mac):

```bash
cd inference
pip install -r requirements.txt
uvicorn src.app:app --reload --port 8080
```

Probar:

**Linux / Mac:**

```bash
curl http://localhost:8080/health
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{
  "years_at_company": 3, "performance_rating": 3, "no_of_promotions": 1,
  "overtime": 0, "edu_level": 2, "no_of_dependents": 0, "job_level": 2,
  "company_size": 2, "company_tenure": 5, "remote_work": 0,
  "company_reputation": 3, "overall_satisfaction": 3, "opportunities": 2,
  "annual_income": 2, "age_group": 2
}'
```

**Windows (PowerShell):** usa `curl.exe` (no el alias `curl` de PowerShell, que en realidad es `Invoke-WebRequest` y no acepta los mismos flags):

```powershell
curl.exe http://localhost:8080/health
curl.exe -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"years_at_company": 3, "performance_rating": 3, "no_of_promotions": 1, "overtime": 0, "edu_level": 2, "no_of_dependents": 0, "job_level": 2, "company_size": 2, "company_tenure": 5, "remote_work": 0, "company_reputation": 3, "overall_satisfaction": 3, "opportunities": 2, "annual_income": 2, "age_group": 2}'
```

O con Docker (el contexto de build es `inference/`, así que el `model.pkl` debe existir en `inference/artifacts/` **antes** de construir la imagen; mismos comandos en Windows y Linux/Mac):

```bash
docker build -t attrition-inference:1.0.0 ./inference
docker run -p 8080:8080 attrition-inference:1.0.0
```

## 5. Frontend

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

Por defecto llama al endpoint de inferencia configurado en `frontend/app.py` — apunta a `http://localhost:8080/predict` en local, o a la URL del servicio de KServe en Kubernetes.

## 6. Despliegue en Kubernetes / KServe

```bash
kubectl apply -f k8s/inference.yaml   # InferenceService (KServe)
kubectl apply -f k8s/deployment.yaml  # Frontend + Service
```

KServe expone el predictor como `<nombre-del-InferenceService>-predictor.<namespace>.svc.cluster.local`. Con `metadata.name: employee-attrition` en `inference.yaml`, el endpoint interno es `employee-attrition-predictor.default.svc.cluster.local`, que es justamente el valor configurado en `MODEL_ENDPOINT` dentro de `k8s/deployment.yaml`.

## Notas para el instructor

- El dataset no contiene el valor `"Executive"` para `Job Level`, aunque el esquema de validación y el encoding lo contemplan — es un buen ejemplo en vivo para hablar de *validación de esquemas* y *manejo de categorías no vistas*.
- `04_tuning.py` guarda el modelo final envuelto en un `types.SimpleNamespace` que solo expone `.predict` (en realidad `predict_proba`), para simplificar el contrato con `inference/src/predictor.py`. Es un buen punto para discutir el "contrato" entre entrenamiento y serving.
- Las versiones en los `requirements.txt` están sin fijar (unpinned) a propósito para simplicidad del bootcamp; para un entorno reproducible, congela versiones (`pip freeze`) antes de cada cohorte.
