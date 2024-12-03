import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Análisis por SKU y Fecha")

# Subida del archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Leer el archivo con encoding ISO-8859-1 y separador ';'
        df = pd.read_csv(uploaded_file, sep=';', quotechar='"', encoding='ISO-8859-1')
        st.write("Archivo leído correctamente.")
        st.write("Total de filas originales:", len(df))
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    # Mostrar columnas detectadas
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
        # Revisar valores únicos en 'sku'
        st.write("Valores únicos en 'sku':")
        st.write(df["sku"].unique())

        # Filtrar filas relacionadas con SKU "237"
        st.subheader("Filas relacionadas con SKU 237 (incluyendo nulos o ceros):")
        sku_237_df = df[df["sku"] == "237"]
        st.dataframe(sku_237_df)

        # Convertir 'cantidad' a numérico
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
        st.write("Estadísticas de la columna 'cantidad':")
        st.write(df["cantidad"].describe())

        # Revisar filas con valores nulos en 'cantidad'
        st.write("Filas con valores nulos o no válidos en 'cantidad':")
        st.dataframe(df[df["cantidad"].isnull()])

        # Convertir 'fecha_venta' a formato datetime
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Filtrar filas con valores válidos en 'cantidad'
        df = df.dropna(subset=["cantidad", "fecha_venta"])
        df = df[df["cantidad"] > 0]

        # Agrupar por fecha y SKU, sumando las cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"])["cantidad"].sum().reset_index()
        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total"]

        # Verificar totales para SKU "237"
        total_original = sku_237_df["cantidad"].sum()
        total_procesado = grouped_data[grouped_data["SKU"] == "237"]["Cantidad Total"].sum()
        st.write(f"Total original para SKU 237: {total_original}")
        st.write(f"Total procesado para SKU 237: {total_procesado}")

        # Mostrar datos agrupados
        st.subheader("Datos Agrupados por Fecha y SKU:")
        st.dataframe(grouped_data)

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
