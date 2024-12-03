import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Cantidad por SKU y Fecha")

# Subida del archivo CSV
uploaded_file = st.file_uploader("Sube un archivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Detectar y leer el archivo con encoding 'ISO-8859-1' y separador ';'
        df = pd.read_csv(uploaded_file, sep=';', quotechar='"', encoding='ISO-8859-1')
        st.write("Archivo leído correctamente.")
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        st.stop()

    # Mostrar columnas detectadas y vista previa
    st.write("Columnas detectadas:", list(df.columns))
    st.write("Vista previa del archivo:")
    st.dataframe(df.head())

    try:
        # Renombrar columnas para que coincidan con las esperadas
        column_mapping = {
            "Fecha": "fecha_venta",
            "SKU": "sku",
            "Cantidad Producto": "cantidad"
        }
        df.rename(columns=column_mapping, inplace=True)

        # Validar columnas requeridas
        required_columns = ["fecha_venta", "sku", "cantidad"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
            st.stop()

        # Convertir columnas a los tipos adecuados
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Agrupar por fecha_venta y SKU, sumando cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"]).agg({
            "cantidad": "sum"
        }).reset_index()

        # Renombrar columnas para claridad
        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total"]

        # Mostrar los datos procesados
        st.subheader("Cantidad de Productos por SKU y Fecha:")
        st.dataframe(grouped_data)

        # Exportar los datos procesados a un archivo CSV
        csv = grouped_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Archivo CSV",
            data=csv,
            file_name="cantidad_por_sku_y_fecha.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error procesando el archivo: {e}")
else:
    st.info("Por favor, sube un archivo CSV para comenzar.")
