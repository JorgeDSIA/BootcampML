"""Etapa 3 de entrenamiento: validación cruzada (cross-validation).

Confirma que el modelo es estable (no memorizó los datos de un solo split)
entrenando y evaluándolo 5 veces con distintas divisiones del dataset.
"""
import pandas as pd
import joblib
from sklearn.model_selection import cross_val_score, StratifiedKFold
from config.paths import PREPROCESSED_TRAIN_PATH, MODEL_PATH


def cv_data(X_train, y_train):
    """Corre validación cruzada de 5 folds y retorna los puntajes de Recall."""
    pipeline = joblib.load(MODEL_PATH)

    # 5 folds, cada uno manteniendo la misma proporción de clases (StratifiedKFold)
    strat_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=strat_cv, scoring='recall')

    print(f"Strat cv score: {cv_scores.mean() * 100}")
    return cv_scores


if __name__ == "__main__":
    df_train = pd.read_csv(PREPROCESSED_TRAIN_PATH)

    X_train = df_train.drop(columns=['Attrition'])
    y_train = df_train['Attrition']

    cv_data(X_train, y_train)
