import streamlit as st
import pandas as pd
import numpy as np
import io

# -----------------------------------------------
# Títulos
st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Facultad de Ciencias Económicas y Empresariales</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Instituto de Desarrollo Sostenible</h4>", unsafe_allow_html=True)
st.title("Calculadora de Exclusión Digital y Movilidad Social")
st.subheader("Herramienta para el análisis de la brecha digital y oportunidades de desarrollo social.")

# Descripción
st.markdown("""
Esta aplicación permite estimar indicadores de exclusión digital y movilidad social a partir de datos individuales o archivos Excel.
""", unsafe_allow_html=True)

# -----------------------------------------------
# Modo de uso
modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

# -----------------------------------------------
# Modo Ingreso Individual
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

    # -----------------------------------------------
    # Cálculos
    subindice_acceso_computadora = 0 if acceso_computadora == 'No' else 1
    subindice_acceso_internet = 0 if acceso_internet == 'No' else 1
    subindice_capacitacion_tic = 0 if capacitacion_tic == 'No' else 1

    subindice_total_digital = subindice_acceso_computadora + subindice_acceso_internet + subindice_capacitacion_tic
    indice_ordinal = subindice_total_digital  # 0 a 3
    vulnerabilidad_digital = (3 - subindice_total_digital) / 3 * 100

    indice_binario = 1 if subindice_total_digital == 0 else 0

    vulnerabilidad_movilidad = 0
    if nivel_educativo in ['Sin instrucción', 'Primario incompleto']:
        vulnerabilidad_movilidad += 50
    if capacitacion_tic == 'No':
        vulnerabilidad_movilidad += 50
    if vulnerabilidad_movilidad > 100:
        vulnerabilidad_movilidad = 100

    # -----------------------------------------------
    # Mostrar resultados
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

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        resultados.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="Descargar resultados individuales en Excel",
        data=output,
        file_name='resultados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -----------------------------------------------
# Modo por Lote
else:
    st.header('Carga de Datos por Lote')
    archivo = st.file_uploader('Subí un archivo Excel (.xlsx)', type='xlsx')

    if archivo is not None:
        df = pd.read_excel(archivo)

        def calcular_indices(row):
            sub_acceso_computadora = 0 if row['acceso_computadora'] == 'No' else 1
            sub_acceso_internet = 0 if row['acceso_internet'] == 'No' else 1
            sub_capacitacion_tic = 0 if row['capacitacion_tic'] == 'No' else 1

            sub_total = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic
            indice_binario = 1 if sub_total == 0 else 0
            indice_ordinal = sub_total
            vulnerabilidad_digital = (3 - sub_total) / 3 * 100

            vulnerabilidad_movilidad = 0
            if row['nivel_educativo'] in ['Sin instrucción', 'Primario incompleto']:
                vulnerabilidad_movilidad += 50
            if row['capacitacion_tic'] == 'No':
                vulnerabilidad_movilidad += 50
            if vulnerabilidad_movilidad > 100:
                vulnerabilidad_movilidad = 100

            return pd.Series([indice_binario, indice_ordinal, vulnerabilidad_digital, vulnerabilidad_movilidad],
                             index=['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad'])

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


