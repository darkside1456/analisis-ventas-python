from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


ARCHIVO_CSV = "ventas.csv"
CARPETA_SALIDA = Path("resultados")
COLUMNAS_REQUERIDAS = {
    "Fecha",
    "Producto",
    "Categoría",
    "Ciudad",
    "Cantidad",
    "Precio unitario",
    "Total",
}


def convertir_a_numero(serie):
    """Convierte valores como 2,50 o 2.50 en números."""
    resultado = pd.to_numeric(serie, errors="coerce")

    faltantes = resultado.isna()
    texto = (
        serie.loc[faltantes]
        .astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    resultado.loc[faltantes] = pd.to_numeric(texto, errors="coerce")
    return resultado


def cargar_datos():
    """Lee, valida y limpia el archivo de ventas."""
    archivo = Path(ARCHIVO_CSV)

    if not archivo.exists():
        print(f"No se encontró el archivo: {ARCHIVO_CSV}")
        sys.exit(1)

    ventas = pd.read_csv(archivo, sep=";", decimal=",")

    columnas_faltantes = COLUMNAS_REQUERIDAS - set(ventas.columns)
    if columnas_faltantes:
        print("Faltan estas columnas:", ", ".join(columnas_faltantes))
        sys.exit(1)

    ventas["Fecha"] = pd.to_datetime(
        ventas["Fecha"],
        dayfirst=True,
        errors="coerce"
    )

    for columna in ["Cantidad", "Precio unitario", "Total"]:
        ventas[columna] = convertir_a_numero(ventas[columna])

    ventas = ventas.dropna(
        subset=["Fecha", "Producto", "Ciudad", "Cantidad", "Precio unitario"]
    )

    ventas["Total"] = ventas["Total"].fillna(
        ventas["Cantidad"] * ventas["Precio unitario"]
    )

    return ventas


def crear_resumenes(ventas):
    """Crea los resúmenes principales del análisis."""
    por_ciudad = (
        ventas.groupby("Ciudad")["Total"]
        .sum()
        .sort_values(ascending=False)
    )

    por_producto = (
        ventas.groupby("Producto")["Total"]
        .sum()
        .sort_values(ascending=False)
    )

    por_categoria = (
        ventas.groupby("Categoría")["Total"]
        .sum()
        .sort_values(ascending=False)
    )

    return por_ciudad, por_producto, por_categoria


def guardar_resultados(por_ciudad, por_producto, por_categoria):
    """Guarda los resúmenes como archivos CSV."""
    CARPETA_SALIDA.mkdir(exist_ok=True)

    por_ciudad.to_csv(CARPETA_SALIDA / "ventas_por_ciudad.csv")
    por_producto.to_csv(CARPETA_SALIDA / "ventas_por_producto.csv")
    por_categoria.to_csv(CARPETA_SALIDA / "ventas_por_categoria.csv")


def crear_graficos(por_ciudad, por_producto, por_categoria):
    """Crea un panel con tres gráficos."""
    CARPETA_SALIDA.mkdir(exist_ok=True)

    figura, ejes = plt.subplots(3, 1, figsize=(10, 14))

    por_ciudad.plot(kind="bar", ax=ejes[0], color="steelblue")
    ejes[0].set_title("Ventas por ciudad")
    ejes[0].set_xlabel("Ciudad")
    ejes[0].set_ylabel("Ingresos")

    por_producto.plot(kind="bar", ax=ejes[1], color="seagreen")
    ejes[1].set_title("Ventas por producto")
    ejes[1].set_xlabel("Producto")
    ejes[1].set_ylabel("Ingresos")

    por_categoria.plot(kind="bar", ax=ejes[2], color="darkorange")
    ejes[2].set_title("Ventas por categoría")
    ejes[2].set_xlabel("Categoría")
    ejes[2].set_ylabel("Ingresos")

    figura.tight_layout()
    figura.savefig(CARPETA_SALIDA / "panel_ventas.png", dpi=150)
    plt.show()


def main():
    ventas = cargar_datos()
    por_ciudad, por_producto, por_categoria = crear_resumenes(ventas)

    print("\n--- VENTAS POR CIUDAD ---")
    print(por_ciudad)

    print("\n--- VENTAS POR PRODUCTO ---")
    print(por_producto)

    print("\n--- VENTAS POR CATEGORÍA ---")
    print(por_categoria)

    guardar_resultados(por_ciudad, por_producto, por_categoria)
    crear_graficos(por_ciudad, por_producto, por_categoria)

    print("\nProyecto terminado. Revisa la carpeta 'resultados'.")


if __name__ == "__main__":
    main()