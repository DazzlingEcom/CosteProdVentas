import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Procesador de CSV - Inclusión de Fechas Faltantes por Número de Orden")

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
    required_columns = ["fecha_venta", "sku", "cantidad", "Número de orden"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"Faltan las siguientes columnas requeridas: {missing_columns}")
        st.stop()

    try:
        # Convertir 'cantidad' a numérico
        df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")

        # Convertir 'fecha_venta' a formato datetime
        df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce", format='%d/%m/%Y')

        # Identificar filas sin fecha y con fecha
        filas_sin_fecha = df[df["fecha_venta"].isna()]
        filas_con_fecha = df[df["fecha_venta"].notna()]

        # Vincular las fechas faltantes usando 'Número de orden'
        fecha_vinculada = filas_sin_fecha.merge(
            filas_con_fecha[["Número de orden", "fecha_venta"]],
            on="Número de orden",
            how="left"
        )

        # Actualizar las fechas de las filas sin fecha en el dataframe original
        filas_sin_fecha["fecha_venta"] = fecha_vinculada["fecha_venta"]

        # Combinar nuevamente el dataframe
        df_actualizado = pd.concat([filas_con_fecha, filas_sin_fecha])

        # Verificar si quedan filas sin fecha
        filas_sin_fecha_final = df_actualizado[df_actualizado["fecha_venta"].isna()]
        if not filas_sin_fecha_final.empty:
            st.warning(f"Aún hay {len(filas_sin_fecha_final)} filas sin fecha después de la vinculación.")
            st.write("Filas sin fecha:")
            st.dataframe(filas_sin_fecha_final)

        # Agrupar por fecha y SKU, sumando las cantidades
        grouped_data = df_actualizado.groupby(["fecha_venta", "sku"])["cantidad"].sum().reset_index()
        grouped_data.columns = ["Fecha de Venta", "SKU", "Cantidad Total"]

        # Verificar totales para SKU específico
        sku_to_check = "EC_237"
        total_original = df[df["sku"] == sku_to_check]["cantidad"].sum()
        total_procesado = grouped_data[grouped_data["SKU"] == sku_to_check]["Cantidad Total"].sum()
        st.write(f"Total original para SKU {sku_to_check}: {total_original}")
        st.write(f"Total procesado para SKU {sku_to_check}: {total_procesado}")

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
