import streamlit as st
import pandas as pd
import numpy as np
import io

# -----------------------------------------------
# Títulos institucionales
st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Facultad de Ciencias Económicas y Empresariales</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Instituto de Desarrollo Sostenible</h4>", unsafe_allow_html=True)

# Título principal
st.title("Calculadora de Exclusión Digital y Movilidad Social")

# Subtítulo general
st.subheader("Herramienta para el análisis de la brecha digital y oportunidades de desarrollo social.")

# Descripción general
st.markdown("""
Esta aplicación permite estimar indicadores de exclusión digital y movilidad social a partir de datos individuales o archivos Excel.
""", unsafe_allow_html=True)

# Descripción de indicadores
st.markdown("""
**Definición de indicadores calculados:**

- **Índice Binario de Exclusión Digital:**  
  Toma valor 1 si la persona no tiene acceso a computadora, internet ni capacitación TIC; y 0 en caso contrario. Indica exclusión digital completa.

- **Índice Ordinal de Exclusión Digital:**  
  Clasifica el acceso digital en cuatro niveles:
  - 0: Sin acceso a ninguna dimensión digital
  - 1: Acceso a una dimensión digital
  - 2: Acceso a dos dimensiones digitales
  - 3: Acceso completo a todas las dimensiones digitales

- **Porcentaje de Vulnerabilidad Digital:**  
  Mide la magnitud de la exclusión digital en escala de 0% a 100%:
  - 0%: Sin vulnerabilidad digital
  - 100%: Exclusión digital total

- **Porcentaje de Vulnerabilidad de Movilidad Social:**  
  Estima el riesgo de movilidad social reducida:
  - Se calcula según nivel educativo y capacitación TIC.
  - Toma valores entre 0% y 100%.
""", unsafe_allow_html=True)

# -----------------------------------------------
# Selector de modo de uso
modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

# -----------------------------------------------
# Modo de ingreso individual
if modo == 'Ingreso individual':
    st.header('Ingreso de Datos')
    
    sexo = st.selectbox('Sexo:', ['Varón', 'Mujer'])
    edad = st.number_input('Edad:', min_value=0, max_value=120, value=30)
    nivel_educativo = st.selectbox('Nivel Educativo:', [
        'Sin instrucción', 'Primario incompleto', 'Primario completo',
        'Secundario incompleto', 'Secundario completo',
        'Superior universitario incompleto', 'Superior universitario completo'
    ])
    acceso_computadora = st.selectbox('¿Tiene acceso a computadora?', ['Sí', 'No'])
    acceso_internet = st.selectbox('¿Tiene acceso a internet?', ['Sí', 'No'])
    capacitacion_tic = st.selectbox('¿Tiene capacitación en TIC?', ['Sí', 'No'])
    region = st.selectbox('Región:', ['Gran Buenos Aires', 'Noroeste', 'Noreste', 'Cuyo', 'Pampeana', 'Patagonia'])
    provincia = st.text_input('Provincia (opcional):', '')

    # Cálculo de subíndices digitales
    sub_acceso_computadora = 1 if acceso_computadora == 'Sí' else 0
    sub_acceso_internet = 1 if acceso_internet == 'Sí' else 0
    sub_capacitacion_tic = 1 if capacitacion_tic == 'Sí' else 0

    # Índices de exclusión digital
    sub_total_digital = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic
    indice_ordinal = sub_total_digital  # de 0 a 3
    indice_binario = 1 if sub_total_digital == 0 else 0
    vulnerabilidad_digital = (3 - sub_total_digital) / 3 * 100

    # Índice de vulnerabilidad de movilidad social
    vulnerabilidad_movilidad = 0
    if nivel_educativo in ['Sin instrucción', 'Primario incompleto']:
        vulnerabilidad_movilidad += 50
    if capacitacion_tic == 'No':
        vulnerabilidad_movilidad += 50
    vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

    # Resultados
    st.header('Resultados')
    st.write(f"**Índice Binario de Exclusión Digital:** {indice_binario}")
    st.write(f"**Índice Ordinal de Exclusión Digital:** {indice_ordinal}")
    st.write(f"**Porcentaje de Vulnerabilidad Digital:** {vulnerabilidad_digital:.1f}%")
    st.write(f"**Porcentaje de Vulnerabilidad de Movilidad Social:** {vulnerabilidad_movilidad}%")

    resultados = pd.DataFrame({
        'sexo': [sexo],
        'edad': [edad],
        'nivel_educativo': [nivel_educativo],
        'acceso_computadora': [acceso_computadora],
        'acceso_internet': [acceso_internet],
        'capacitacion_tic': [capacitacion_tic],
        'region': [region],
        'provincia': [provincia],
        'indice_binario': [indice_binario],
        'indice_ordinal': [indice_ordinal],
        'vulnerabilidad_digital': [vulnerabilidad_digital],
        'vulnerabilidad_movilidad': [vulnerabilidad_movilidad]
    })

    # Descargar resultados individuales en Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resultados.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="Descargar resultados individuales en Excel",
        data=output,
        file_name='resultados_individual.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -----------------------------------------------
# Modo de carga por lote
elif modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo = st.file_uploader('Subí un archivo Excel (.xlsx)', type='xlsx')

    if archivo is not None:
        df = pd.read_excel(archivo)

        # Asegurarse de que las columnas estén en minúsculas y sin espacios
        df.rename(columns=lambda x: x.strip().lower().replace(" ", "_"), inplace=True)

        # Verificar la presencia de la columna 'nivel_educativo'
        if 'nivel_educativo' not in df.columns:
            st.error("La columna 'nivel_educativo' no se encuentra en el archivo. Por favor, verifica el nombre.")
        else:
            def calcular_indices(row):
                sub_acceso_computadora = 1 if row['acceso_computadora'] == 'Sí' else 0
                sub_acceso_internet = 1 if row['acceso_internet'] == 'Sí' else 0
                sub_capacitacion_tic = 1 if row['capacitacion_tic'] == 'Sí' else 0

                sub_total = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic
                indice_ordinal = sub_total
                indice_binario = 1 if sub_total == 0 else 0
                vulnerabilidad_digital = (3 - sub_total) / 3 * 100

                vulnerabilidad_movilidad = 0
                if row['nivel_educativo'] in ['Sin instrucción', 'Primario incompleto']:
                    vulnerabilidad_movilidad += 50
                if row['capacitacion_tic'] == 'No':
                    vulnerabilidad_movilidad += 50
                vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

                return pd.Series([
                    indice_binario, indice_ordinal,
                    vulnerabilidad_digital, vulnerabilidad_movilidad
                ], index=[
                    'indice_binario', 'indice_ordinal',
                    'vulnerabilidad_digital', 'vulnerabilidad_movilidad'
                ])

            df[['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']] = df.apply(calcular_indices, axis=1)

            st.success('Datos procesados correctamente')
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)

            st.download_button(
                label="Descargar resultados en Excel",
                data=output,
                file_name='resultados_lote.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )



