"""Etapa 3 del pipeline de datos: análisis exploratorio de datos (EDA).

Genera estadísticas y gráficos para entender la distribución de los datos
antes de limpiarlos y transformarlos en las siguientes etapas.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from config.paths import VALIDATION_PATH, EDA_PATH


def eda_data(df):
    """Imprime estadísticas descriptivas y muestra 4 gráficos de exploración."""
    # Estadísticas básicas por columna (media, min, max, valores únicos, etc.)
    print("Basic Statistics:")
    print(df.describe(include='all'))

    # Gráfico 1: distribución de la edad de los empleados
    plt.figure(figsize=(8, 6))
    sns.histplot(df['Age'], bins=30, kde=True)
    plt.title('Age Distribution')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.show()

    # Gráfico 2: cuántos empleados se quedaron vs. se fueron (balance de clases)
    plt.figure(figsize=(6, 4))
    sns.countplot(x='Attrition', data=df)
    plt.title('Attrition Count')
    plt.xlabel('Attrition')
    plt.ylabel('Count')
    plt.show()

    # Gráfico 3: cómo varía el ingreso mensual según el nivel de puesto
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Job Level', y='Monthly Income', data=df)
    plt.title('Monthly Income by Job Level')
    plt.xlabel('Job Level')
    plt.ylabel('Monthly Income')
    plt.show()

    # Gráfico 4: correlación entre columnas numéricas (ayuda a decidir qué features combinar)
    plt.figure(figsize=(12, 10))
    corr = df.select_dtypes(include=['int64', 'float64']).corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm')
    plt.title('Correlation Heatmap')
    plt.show()

    df.to_csv(EDA_PATH, index=False)  # se guarda igual: el EDA no modifica los datos
    return df

if __name__ == "__main__":
    df = pd.read_csv(VALIDATION_PATH)
    eda_data(df)
