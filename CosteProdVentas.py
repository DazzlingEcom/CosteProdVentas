import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Análisis por SKU y Fecha")

# Subida del archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Detectar y leer el archivo con encoding 'ISO-8859-1' y separador ';'
        df = pd.read_csv(uploaded_file, sep=';', quotechar='"', encoding='ISO-8859-1')
        st.write("Archivo leído correctamente.")
        st.write("Total de filas originales:", len(df))
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    # Mostrar columnas detectadas y vista previa
    st.write("Columnas detectadas:", list(df.columns))
    st.write("Vista previa del archivo:")
    st.dataframe(df.head())

    # Renombrar columnas relevantes
    column_mapping = {"Fecha": "fecha_venta", "SKU": "sku", "Cantidad del producto": "cantidad"}
    df = df.rename(columns=column_mapping)
    st.write("Columnas después del renombramiento:", list(df.columns))

    # Validar que las columnas requeridas existan
    required_columns = ["fecha_venta", "sku", "cantidad"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
        st.stop()

    try:
        # Convertir 'cantidad' a numérico
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")

        # Filtrar las filas con SKU igual a "237" para inspección
        st.subheader("Filas originales para SKU 237")
        st.dataframe(df[df["sku"] == "237"])

        # Convertir 'fecha_venta' a formato datetime
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Filtrar filas con valores nulos o cero en 'cantidad'
        df = df.dropna(subset=["cantidad", "fecha_venta"])
        df = df[df["cantidad"] > 0]

        # Agrupar por fecha y SKU, sumando las cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"])["cantidad"].sum().reset_index()
        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total"]

        # Verificar totales para SKU 237
        total_original = df[df["sku"] == "237"]["cantidad"].sum()
        total_procesado = grouped_data[grouped_data["SKU"] == "237"]["Cantidad Total"].sum()
        st.write(f"Total original para SKU 237: {total_original}")
        st.write(f"Total procesado para SKU 237: {total_procesado}")

        # Mostrar los datos agrupados
        st.subheader("Datos Agrupados por Fecha y SKU:")
        st.dataframe(grouped_data)

        # Exportar archivo intermedio para inspección
        csv_intermedio = df[df["sku"] == "237"].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV Intermedio (SKU 237)",
            data=csv_intermedio,
            file_name="datos_intermedios_sku_237.csv",
            mime="text/csv"
        )

        # Exportar datos agrupados
        csv_final = grouped_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV Agrupado",
            data=csv_final,
            file_name="cantidad_por_sku_fecha.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
