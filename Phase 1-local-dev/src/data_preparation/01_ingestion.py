"""Etapa 1 del pipeline de datos: carga el CSV crudo y lo copia a datasets/processed/.

A partir de aquí, las siguientes etapas nunca vuelven a leer el dataset original.
"""
import pandas as pd
from pandas import DataFrame
from config.paths import RAW_DATA_PATH, INGESTION_PATH


def ingestion() -> DataFrame:
    """Lee el CSV crudo, imprime un resumen (head, shape, info) y guarda una copia."""
    df = pd.read_csv(RAW_DATA_PATH)
    print(df.head(5))  # primeras 5 filas, para confirmar que se cargo bien
    print("------")

    print(f"Shape: {df.shape}")  # (filas, columnas)
    print("------")

    print(f"Information: {df.info()}")  # tipos de dato y nulos por columna
    print("------")
    
    df.to_csv(INGESTION_PATH, index=False)  # copia base para las siguientes etapas
    return df


if __name__ == "__main__":
    ingestion()