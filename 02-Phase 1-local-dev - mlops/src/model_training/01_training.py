"""Etapa 1 de entrenamiento: construye y entrena el pipeline del modelo.

Genera artifacts/model.pkl: un Pipeline de scikit-learn (escalado + Regresión
Logística) listo para evaluar, ajustar (tuning) y servir en inferencia.
"""
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from config.paths import PREPROCESSED_TRAIN_PATH, MODEL_PATH

# Columns that need scaling - must use integer indices for KServe compatibility
# (KServe sends raw numpy arrays, not DataFrames)
NUMERIC_COLS = ['Years at Company', 'Company Tenure', 'RoleStagnationRatio', 'TenureGap']


def train_data(df):
    """Entrena un Pipeline (escalado + Regresión Logística) y lo guarda en MODEL_PATH."""
    X_train = df.drop(columns=['Attrition'])
    y_train = df['Attrition']

    # Get integer indices for numeric columns (required for KServe numpy input)
    numeric_indices = [X_train.columns.get_loc(col) for col in NUMERIC_COLS]

    # Solo se escalan las columnas numéricas; el resto pasa sin cambios (remainder='passthrough')
    preprocessor = ColumnTransformer(
        transformers=[('scaler', StandardScaler(), numeric_indices)],
        remainder='passthrough'
    )

    # class_weight='balanced' compensa que hay más empleados que se quedan que los que se van
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])

    print("Training the model....")
    pipeline.fit(X_train, y_train)
    print("training completed...")

    joblib.dump(pipeline, MODEL_PATH)  # guarda el pipeline completo (preprocesador + clasificador)

    return True


if __name__ == "__main__":
    df_train = pd.read_csv(PREPROCESSED_TRAIN_PATH)
    train_data(df_train)
