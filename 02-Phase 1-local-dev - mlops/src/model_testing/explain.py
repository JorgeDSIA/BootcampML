"""Explicabilidad del modelo con SHAP: no solo "qué" predice, sino "por qué".

A diferencia de 02_evaluation.py (que muestra los coeficientes globales de la
Regresión Logística), este script explica predicciones puntuales: para un
empleado concreto, qué features empujaron la predicción hacia "se va" o
"se queda" y cuánto pesó cada una. Usa artifacts/pipeline.pkl (el pipeline
"crudo", guardado por 04_tuning.py) porque SHAP necesita el preprocesador y el
clasificador por separado, algo que model.pkl (envuelto para inferencia) ya no expone.
"""
import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib
matplotlib.use('Agg')  # backend sin ventana gráfica (útil al correr en servidor/CI)
import matplotlib.pyplot as plt
from config.paths import PREPROCESSED_TRAIN_PATH, PREPROCESSED_TEST_PATH, PIPELINE_PATH, ARTIFACT_DIR


def get_feature_names(pipeline, original_columns):
    """Extrae los nombres de features en el orden que produce el ColumnTransformer (misma lógica que 02_evaluation.py)."""
    ct = pipeline.named_steps['preprocessor']
    feature_names = []
    for name, transformer, indices in ct.transformers_:
        feature_names.extend([original_columns[i] for i in indices])
    return feature_names


def build_explainer(pipeline, X_background, feature_names):
    """Crea un SHAP LinearExplainer sobre el clasificador, usando datos ya preprocesados como fondo."""
    preprocessor = pipeline.named_steps['preprocessor']
    classifier = pipeline.named_steps['classifier']
    background = preprocessor.transform(X_background)
    return shap.LinearExplainer(classifier, background, feature_names=feature_names)


def explain_global(pipeline, explainer, X_sample, feature_names, top_n=10):
    """Calcula SHAP values sobre X_sample y muestra qué features pesan más, en promedio, en todo el dataset."""
    preprocessor = pipeline.named_steps['preprocessor']
    sample = preprocessor.transform(X_sample)
    shap_values = explainer.shap_values(sample)

    mean_abs = np.abs(shap_values).mean(axis=0)
    ranking = sorted(zip(feature_names, mean_abs), key=lambda x: x[1], reverse=True)[:top_n]

    print("=== Importancia global de features (SHAP, impacto promedio |valor|) ===")
    for name, value in ranking:
        print(f"{name:<25} {value:.4f}")

    plt.figure(figsize=(9, 6))
    shap.summary_plot(shap_values, sample, feature_names=feature_names, plot_type="bar", show=False)
    plot_path = ARTIFACT_DIR / "shap_summary.png"
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"\nGráfico guardado en: {plot_path}")


def explain_instance(pipeline, explainer, feature_names, record: dict, top_n=5):
    """Explica una predicción puntual: qué features empujaron el resultado y en qué dirección."""
    preprocessor = pipeline.named_steps['preprocessor']
    classifier = pipeline.named_steps['classifier']

    df_input = pd.DataFrame([record])
    transformed = preprocessor.transform(df_input)

    p_leave = classifier.predict_proba(transformed)[0][1]
    shap_values = explainer.shap_values(transformed)[0]  # contribución de cada feature, en log-odds
    base_value = explainer.expected_value
    if isinstance(base_value, np.ndarray):
        base_value = base_value[0]

    contributions = sorted(zip(feature_names, shap_values), key=lambda x: abs(x[1]), reverse=True)[:top_n]

    print("\n=== Por qué el modelo predijo esto ===")
    print(f"Probabilidad de renuncia: {p_leave:.4f}")
    print(f"Valor base (log-odds promedio del dataset): {base_value:.4f}")
    for name, value in contributions:
        direction = "aumenta el riesgo de renuncia" if value > 0 else "reduce el riesgo de renuncia"
        print(f"  {name:<25} {value:+.4f}  -> {direction}")


if __name__ == "__main__":
    pipeline = joblib.load(PIPELINE_PATH)

    df_train = pd.read_csv(PREPROCESSED_TRAIN_PATH)
    df_test = pd.read_csv(PREPROCESSED_TEST_PATH)

    X_train = df_train.drop(columns=['Attrition'])
    X_test = df_test.drop(columns=['Attrition'])

    feature_names = get_feature_names(pipeline, X_train.columns.tolist())

    # fondo pequeño para acelerar el LinearExplainer (no hace falta todo el train set)
    background = X_train.sample(n=min(100, len(X_train)), random_state=42)
    explainer = build_explainer(pipeline, background, feature_names)

    explain_global(pipeline, explainer, X_test, feature_names)

    # explica el primer caso del test set como ejemplo
    sample_record = X_test.iloc[0].to_dict()
    explain_instance(pipeline, explainer, feature_names, sample_record)
