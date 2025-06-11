import streamlit as st
import pandas as pd
import numpy as np
import io

# -----------------------------------------------
# Títulos institucionales
st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Facultad de Ciencias Económicas y Empresariales</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Instituto de Desarrollo Sostenible</h4>", unsafe_allow_html=True)

st.title("Calculadora de Exclusión Digital y Movilidad Social")
st.subheader("Herramienta para el análisis de la brecha digital y oportunidades de desarrollo social.")

st.markdown("""
Esta aplicación permite estimar indicadores de exclusión digital y movilidad social a partir de datos individuales o archivos Excel.
""", unsafe_allow_html=True)

st.markdown("""
**Definición de indicadores calculados:**
- **Índice Binario de Exclusión Digital:** 1 si la persona está completamente excluida digitalmente; 0 en caso contrario.
- **Índice Ordinal de Exclusión Digital (%):** Expresa el nivel de acceso digital en porcentaje (10%-100%).
- **Porcentaje de Vulnerabilidad Digital (%):** Cuantifica la exclusión digital en escala de 10%-100%.
- **Porcentaje de Vulnerabilidad de Movilidad Social (%):** Calcula el riesgo de movilidad social reducida (0%-100%).
""", unsafe_allow_html=True)

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
    region = st.selectbox('Región:', ['Gran Buenos Aires', 'Pampeana', 'Noroeste', 'Noreste', 'Cuyo', 'Patagonia'])
    provincia = st.text_input('Provincia (opcional):', '')

    sub_acceso_computadora = 1 if acceso_computadora == 'Sí' else 0
    sub_acceso_internet = 1 if acceso_internet == 'Sí' else 0
    sub_capacitacion_tic = 1 if capacitacion_tic == 'Sí' else 0

    sub_total_digital = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic

    indice_ordinal = ((sub_total_digital) / 3 * 90) + 10
    indice_binario = 1 if sub_total_digital == 0 else 0
    vulnerabilidad_digital = ((3 - sub_total_digital) / 3 * 90) + 10

    # Vulnerabilidad de Movilidad Social (fraccionada)
    puntaje_nivel_ed = 0
    if nivel_educativo == 'Sin instrucción':
        puntaje_nivel_ed = 7
    elif nivel_educativo == 'Primario incompleto':
        puntaje_nivel_ed = 6
    elif nivel_educativo == 'Primario completo':
        puntaje_nivel_ed = 5
    elif nivel_educativo == 'Secundario incompleto':
        puntaje_nivel_ed = 4
    elif nivel_educativo == 'Secundario completo':
        puntaje_nivel_ed = 3
    elif nivel_educativo == 'Superior universitario incompleto':
        puntaje_nivel_ed = 2
    elif nivel_educativo == 'Superior universitario completo':
        puntaje_nivel_ed = 1

    vulnerabilidad_educativa = (puntaje_nivel_ed / 7) * 50  # 0 a 50%
    vulnerabilidad_tic = 50 if capacitacion_tic == 'No' else 0

    vulnerabilidad_movilidad = vulnerabilidad_educativa + vulnerabilidad_tic
    vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

    st.header('Resultados')
    st.write(f"**Índice Binario de Exclusión Digital:** {indice_binario}")
    st.write(f"**Índice Ordinal de Exclusión Digital:** {indice_ordinal:.1f}%")
    st.write(f"**Porcentaje de Vulnerabilidad Digital:** {vulnerabilidad_digital:.1f}%")
    st.write(f"**Porcentaje de Vulnerabilidad de Movilidad Social:** {vulnerabilidad_movilidad:.1f}%")

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
        file_name='resultados_individual.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -----------------------------------------------
# Modo de carga por lote (Excel)
elif modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo_consolidado = st.file_uploader('Subí el archivo consolidado (.xlsx) del 4º trimestre', type='xlsx')

    if archivo_consolidado:
        try:
            df = pd.read_excel(archivo_consolidado)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # Mapeo de variables TIC
            df['acceso_computadora'] = df['ip_iii_04'].map({1: 'Sí', 2: 'No'})
            df['acceso_internet'] = df['ip_iii_05'].map({1: 'Sí', 2: 'No'})
            df['capacitacion_tic'] = df['ip_iii_06'].map({1: 'Sí', 2: 'No'})

            # Mapeo de nivel educativo
            mapeo_nivel_ed = {
                1: 'Sin instrucción',
                2: 'Primario incompleto',
                3: 'Primario completo',
                4: 'Secundario incompleto',
                5: 'Secundario completo',
                6: 'Superior universitario incompleto',
                7: 'Superior universitario completo'
            }
            df['nivel_educativo'] = df['nivel_ed'].map(mapeo_nivel_ed)

            def calcular_indices(row):
                sub_acceso_computadora = 1 if row['acceso_computadora'] == 'Sí' else 0
                sub_acceso_internet = 1 if row['acceso_internet'] == 'Sí' else 0
                sub_capacitacion_tic = 1 if row['capacitacion_tic'] == 'Sí' else 0
                sub_total = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic

                indice_ordinal = ((sub_total) / 3 * 90) + 10
                indice_binario = 1 if sub_total == 0 else 0
                vulnerabilidad_digital = ((3 - sub_total) / 3 * 90) + 10

                puntaje_nivel_ed = 0
                if row['nivel_educativo'] == 'Sin instrucción':
                    puntaje_nivel_ed = 7
                elif row['nivel_educativo'] == 'Primario incompleto':
                    puntaje_nivel_ed = 6
                elif row['nivel_educativo'] == 'Primario completo':
                    puntaje_nivel_ed = 5
                elif row['nivel_educativo'] == 'Secundario incompleto':
                    puntaje_nivel_ed = 4
                elif row['nivel_educativo'] == 'Secundario completo':
                    puntaje_nivel_ed = 3
                elif row['nivel_educativo'] == 'Superior universitario incompleto':
                    puntaje_nivel_ed = 2
                elif row['nivel_educativo'] == 'Superior universitario completo':
                    puntaje_nivel_ed = 1

                vulnerabilidad_educativa = (puntaje_nivel_ed / 7) * 50
                vulnerabilidad_tic = 50 if row['capacitacion_tic'] == 'No' else 0

                vulnerabilidad_movilidad = vulnerabilidad_educativa + vulnerabilidad_tic
                vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

                return pd.Series([
                    indice_binario, indice_ordinal,
                    vulnerabilidad_digital, vulnerabilidad_movilidad
                ], index=[
                    'indice_binario', 'indice_ordinal',
                    'vulnerabilidad_digital', 'vulnerabilidad_movilidad'
                ])

            df[['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']] = df.apply(calcular_indices, axis=1)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)

            st.download_button(
                label='Descargar resultados en Excel',
                data=output,
                file_name='resultados_lote.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

