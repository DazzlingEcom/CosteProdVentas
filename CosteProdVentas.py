import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Manejo de Filas Excluidas")

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
        # Convertir 'cantidad' a numérico
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
        st.write("Estadísticas de la columna 'cantidad':")
        st.write(df["cantidad"].describe())

        # Convertir 'fecha_venta' a formato datetime
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Identificar y mostrar filas excluidas
        filas_excluidas = df[df["cantidad"].isnull() | df["fecha_venta"].isnull()]
        st.subheader("Filas excluidas durante el procesamiento:")
        st.dataframe(filas_excluidas)

        # Opcional: completar valores nulos en 'cantidad' con 0
        if st.checkbox("Incluir filas excluidas con correcciones (cantidad=0, fecha=01/01/2000)"):
            filas_excluidas["cantidad"].fillna(0, inplace=True)
            filas_excluidas["fecha_venta"].fillna(pd.Timestamp("2000-01-01"), inplace=True)
            df = pd.concat([df.drop(filas_excluidas.index), filas_excluidas])
            st.write("Filas excluidas reintegradas con valores corregidos.")

        # Filtrar filas válidas
        df = df.dropna(subset=["cantidad", "fecha_venta"])
        df = df[df["cantidad"] > 0]

        # Agrupar por fecha y SKU, sumando las cantidades
        grouped_data = df.groupby(["fecha_venta", "sku"])["cantidad"].sum().reset_index()
        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total"]

        # Verificar totales para SKU EC_237
        total_original = df[df["sku"] == "EC_237"]["cantidad"].sum()
        total_procesado = grouped_data[grouped_data["SKU"] == "EC_237"]["Cantidad Total"].sum()
        st.write(f"Total original para SKU EC_237: {total_original}")
        st.write(f"Total procesado para SKU EC_237: {total_procesado}")

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
