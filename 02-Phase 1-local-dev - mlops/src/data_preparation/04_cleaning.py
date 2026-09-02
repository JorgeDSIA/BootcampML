"""Etapa 4 del pipeline de datos: limpieza básica (duplicados y nulos).

Este script solo reporta duplicados/nulos por consola; no los elimina ni
rellena automáticamente (esa decisión queda a criterio del Data Scientist).
"""
import pandas as pd
from config.paths import EDA_PATH, CLEANING_PATH


def clean_data(df):
    """Reporta filas duplicadas y valores faltantes, y guarda el dataset."""
    print("--- Find duplicates ---")
    df_duplicate = df.duplicated()  # True/False por fila: es un duplicado?
    print(f"Number of duplicate rows: {df_duplicate.sum()}")

    print("--- Find Missing/Null values ---")
    missing_values = df.isnull().sum()  # cantidad de nulos por columna
    print(f"Missing values: {missing_values}")

    df.to_csv(CLEANING_PATH, index=False)

    return df


if __name__ == "__main__":
    df = pd.read_csv(EDA_PATH)
    clean_data(df)
