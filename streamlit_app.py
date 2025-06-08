import streamlit as st
import pandas as pd
import io

# Título institucional
st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Facultad de Ciencias Económicas y Empresariales</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Instituto de Desarrollo Sostenible</h4>", unsafe_allow_html=True)

st.title("Calculadora de Exclusión Digital y Movilidad Social")

# Subtítulo general
st.subheader("Herramienta para el análisis de la brecha digital y su relación con las oportunidades de desarrollo social.")

# Descripción general
st.markdown("""
Esta aplicación permite estimar indicadores clave de exclusión digital y movilidad social a partir de los datos de cada persona o de archivos Excel con múltiples registros.

**Los principales indicadores calculados son:**
- **Índice Binario de Exclusión Digital**: identifica si una persona está completamente excluida digitalmente.
- **Índice Ordinal de Exclusión Digital**: clasifica el nivel de acceso digital en tres categorías: sin acceso, acceso parcial y acceso completo.
- **Porcentaje de Vulnerabilidad Digital**: mide la magnitud de la exclusión digital en una escala de 0 a 100%.
- **Porcentaje de Vulnerabilidad de Movilidad Social**: estima el riesgo de que la persona tenga dificultades para mejorar sus condiciones de vida en función de su nivel educativo, capacitación TIC y exclusión digital.
""", unsafe_allow_html=True)

# Selector de modo de uso
modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

# (Resto del código se mantiene igual...)


if modo == 'Ingreso individual':
    st.header('Ingreso de Datos por Persona')
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
    region = st.selectbox('Región:', [
        'Gran Buenos Aires', 'Noroeste', 'Noreste', 'Cuyo', 'Pampeana', 'Patagonia'
    ])
    provincia = st.text_input('Provincia (opcional):', '')

    if st.button('Calcular Índices'):
        # Índice binario
        indice_binario = 1 if (acceso_computadora == 'No' and acceso_internet == 'No') else 0

        # Índice ordinal
        if acceso_computadora == 'Sí' and acceso_internet == 'Sí':
            indice_ordinal = 2
        elif acceso_computadora == 'Sí' or acceso_internet == 'Sí':
            indice_ordinal = 1
        else:
            indice_ordinal = 0

        # Vulnerabilidad digital (escalonado)
        if acceso_computadora == 'No' and acceso_internet == 'No':
            vulnerabilidad_digital = 100
        elif acceso_computadora == 'No' or acceso_internet == 'No':
            vulnerabilidad_digital = 80
        else:
            vulnerabilidad_digital = 0

        if capacitacion_tic == 'No' and vulnerabilidad_digital < 100:
            vulnerabilidad_digital += 20
        vulnerabilidad_digital = min(vulnerabilidad_digital, 100)

        # Vulnerabilidad movilidad
        vulnerabilidad_movilidad = 0
        if nivel_educativo in ['Sin instrucción', 'Primario incompleto', 'Primario completo']:
            vulnerabilidad_movilidad += 40
        if capacitacion_tic == 'No':
            vulnerabilidad_movilidad += 30
        if indice_binario == 1:
            vulnerabilidad_movilidad += 30
        vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

        st.header("Resultados del Cálculo")

        st.subheader("Índice Binario de Exclusión Digital")
        st.markdown("""
        Este índice identifica si una persona está completamente excluida digitalmente:
        - **1:** Sin acceso a computadora ni internet en el hogar.
        - **0:** Con acceso a al menos uno de los dos.
        """)
        st.write(f"**Resultado:** {indice_binario}")

        st.subheader("Índice Ordinal de Exclusión Digital")
        st.markdown("""
        Mide el nivel de acceso digital:
        - **0:** Sin acceso a computadora ni internet.
        - **1:** Acceso parcial (solo computadora o solo internet).
        - **2:** Acceso completo (ambos servicios).
        """)
        st.write(f"**Resultado:** {indice_ordinal}")

        st.subheader("Porcentaje de Vulnerabilidad Digital")
        st.markdown("""
        Refleja el riesgo de exclusión digital en una escala de 0% a 100%.
        Se incrementa si la persona no tiene capacitación en TIC.
        """)
        st.write(f"**Resultado:** {vulnerabilidad_digital}%")

        st.subheader("Porcentaje de Vulnerabilidad de Movilidad Social")
        st.markdown("""
        Calcula el riesgo de dificultades para mejorar las condiciones de vida considerando:
        - Nivel educativo.
        - Capacitación en TIC.
        - Exclusión digital.
        """)
        st.write(f"**Resultado:** {vulnerabilidad_movilidad}%")

elif modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo = st.file_uploader('Subí un archivo Excel (.xlsx)', type='xlsx')

    if archivo is not None:
        df = pd.read_excel(archivo)

        def calcular_indices(row):
            compu = row['acceso_computadora']
            internet = row['acceso_internet']
            educ = row['nivel_educativo']
            tic = row['capacitacion_tic']

            # Índice binario
            binario = 1 if (compu == 'No' and internet == 'No') else 0

            # Índice ordinal
            if compu == 'Sí' and internet == 'Sí':
                ordinal = 2
            elif compu == 'Sí' or internet == 'Sí':
                ordinal = 1
            else:
                ordinal = 0

            # Vulnerabilidad digital (escalonado)
            if compu == 'No' and internet == 'No':
                vuln_digital = 100
            elif compu == 'No' or internet == 'No':
                vuln_digital = 80
            else:
                vuln_digital = 0

            if tic == 'No' and vuln_digital < 100:
                vuln_digital += 20
            vuln_digital = min(vuln_digital, 100)

            # Vulnerabilidad movilidad
            vuln_movilidad = 0
            if educ in ['Sin instrucción', 'Primario incompleto', 'Primario completo']:
                vuln_movilidad += 40
            if tic == 'No':
                vuln_movilidad += 30
            if binario == 1:
                vuln_movilidad += 30
            vuln_movilidad = min(vuln_movilidad, 100)

            return pd.Series([binario, ordinal, vuln_digital, vuln_movilidad])

        df[['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']] = df.apply(calcular_indices, axis=1)

        st.success('Datos procesados correctamente')
        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label='Descargar resultados en Excel',
            data=output,
            file_name='datos_lote_resultados.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
