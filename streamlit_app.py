import streamlit as st
import pandas as pd
import io

# -----------------------------------------------
# Título institucional
st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: white;'>Facultad de Ciencias Económicas y Empresariales</h3>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>Instituto de Desarrollo Sostenible</h4>", unsafe_allow_html=True)

# Título principal
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

# -----------------------------------------------
# Selector de modo de uso
modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

# -----------------------------------------------
# Modo de ingreso individual
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
    region = st.selectbox('Región:', ['Gran Buenos Aires', 'Noroeste', 'Noreste', 'Cuyo', 'Pampeana', 'Patagonia'])
    provincia = st.text_input('Provincia (opcional):', '')

    # Cálculo de indicadores
    indice_binario = 1 if acceso_computadora == 'No' and acceso_internet == 'No' else 0

    if acceso_computadora == 'No' and acceso_internet == 'No':
        indice_ordinal = 0
    elif acceso_computadora == 'Sí' and acceso_internet == 'Sí':
        indice_ordinal = 2
    else:
        indice_ordinal = 1

    vulnerabilidad_digital = indice_ordinal * 50  # 0%, 50%, 100% según el índice ordinal

    # Ejemplo de índice de movilidad social (simplificado)
    vulnerabilidad_movilidad = 0
    if nivel_educativo in ['Sin instrucción', 'Primario incompleto']:
        vulnerabilidad_movilidad += 50
    if capacitacion_tic == 'No':
        vulnerabilidad_movilidad += 50
    if vulnerabilidad_movilidad > 100:
        vulnerabilidad_movilidad = 100

    st.header('Resultados del Cálculo')
    st.write(f"**Índice Binario de Exclusión Digital:** {indice_binario}")
    st.write(f"**Índice Ordinal de Exclusión Digital:** {indice_ordinal}")
    st.write(f"**Porcentaje de Vulnerabilidad Digital:** {vulnerabilidad_digital}%")
    st.write(f"**Porcentaje de Vulnerabilidad de Movilidad Social:** {vulnerabilidad_movilidad}%")

    # Crear DataFrame de resultados
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
        file_name='resultados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

# -----------------------------------------------
# Modo por lote
elif modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo = st.file_uploader('Subí un archivo Excel (.xlsx)', type='xlsx')

    if archivo is not None:
        df = pd.read_excel(archivo)

        # Procesar cada fila
        df['indice_binario'] = df.apply(lambda row: 1 if row['acceso_computadora'] == 'No' and row['acceso_internet'] == 'No' else 0, axis=1)
        df['indice_ordinal'] = df.apply(lambda row: 0 if row['acceso_computadora'] == 'No' and row['acceso_internet'] == 'No'
                                        else 2 if row['acceso_computadora'] == 'Sí' and row['acceso_internet'] == 'Sí'
                                        else 1, axis=1)
        df['vulnerabilidad_digital'] = df['indice_ordinal'] * 50

        def calcular_movilidad(row):
            vulnerabilidad = 0
            if row['nivel_educativo'] in ['Sin instrucción', 'Primario incompleto']:
                vulnerabilidad += 50
            if row['capacitacion_tic'] == 'No':
                vulnerabilidad += 50
            return min(vulnerabilidad, 100)

        df['vulnerabilidad_movilidad'] = df.apply(calcular_movilidad, axis=1)

        st.success('Datos procesados correctamente')
        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Descargar resultados en Excel",
            data=output,
            file_name='resultados.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

