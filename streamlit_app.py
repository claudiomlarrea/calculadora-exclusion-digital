import streamlit as st
import pandas as pd
import io

st.title('Calculadora de Exclusión Digital y Movilidad Social')

# --- Selector de modo de uso ---
modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

if modo == 'Ingreso individual':
    st.header('Ingreso de Datos por Persona')

    sexo = st.selectbox('Sexo:', ['Varón', 'Mujer'])
    edad = st.number_input('Edad:', min_value=0, max_value=120, value=30)
    nivel_educativo = st.selectbox('Nivel Educativo:', [
        'Sin instrucción',
        'Primario incompleto',
        'Primario completo',
        'Secundario incompleto',
        'Secundario completo',
        'Superior universitario incompleto',
        'Superior universitario completo'
    ])
    acceso_computadora = st.selectbox('¿Tiene acceso a computadora?', ['Sí', 'No'])
    acceso_internet = st.selectbox('¿Tiene acceso a internet?', ['Sí', 'No'])
    capacitacion_tic = st.selectbox('¿Tiene capacitación en TIC?', ['Sí', 'No'])
    region = st.selectbox('Región:', [
        'Gran Buenos Aires', 'Noroeste', 'Noreste', 'Cuyo', 'Pampeana', 'Patagonia'
    ])
    provincia = st.text_input('Provincia (opcional):', '')

    if st.button('Calcular Índices'):
        indice_binario = 1 if (acceso_computadora == 'No' and acceso_internet == 'No') else 0

        if acceso_computadora == 'Sí' and acceso_internet == 'Sí':
            indice_ordinal = 2
        elif acceso_computadora == 'Sí' or acceso_internet == 'Sí':
            indice_ordinal = 1
        else:
            indice_ordinal = 0

        vulnerabilidad_digital = 100 if indice_binario == 1 else 50 if indice_ordinal == 1 else 0

        vulnerabilidad_movilidad = 0
        if nivel_educativo in ['Sin instrucción', 'Primario incompleto', 'Primario completo']:
            vulnerabilidad_movilidad += 40
        if capacitacion_tic == 'No':
            vulnerabilidad_movilidad += 30
        if indice_binario == 1:
            vulnerabilidad_movilidad += 30
        vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

        if edad <= 14:
            grupo_etario = '0-14'
        elif edad <= 24:
            grupo_etario = '15-24'
        elif edad <= 34:
            grupo_etario = '25-34'
        elif edad <= 44:
            grupo_etario = '35-44'
        elif edad <= 54:
            grupo_etario = '45-54'
        elif edad <= 64:
            grupo_etario = '55-64'
        else:
            grupo_etario = '65+'

        st.header('Resultados del Cálculo')
        st.write(f'**Índice Binario de Exclusión Digital:** {indice_binario}')
        st.write(f'**Índice Ordinal de Exclusión Digital:** {indice_ordinal}')
        st.write(f'**Porcentaje de Vulnerabilidad Digital:** {vulnerabilidad_digital}%')
        st.write(f'**Porcentaje de Vulnerabilidad de Movilidad Social:** {vulnerabilidad_movilidad}%')
        st.write(f'**Clasificación Grupal (Edad):** {grupo_etario}')
        st.write(f'**Región:** {region}')
        st.write(f'**Provincia:** {provincia if provincia else "No especificada"}')

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

            binario = 1 if (compu == 'No' and internet == 'No') else 0
            ordinal = 2 if (compu == 'Sí' and internet == 'Sí') else 1 if (compu == 'Sí' or internet == 'Sí') else 0
            vuln_digital = 100 if binario == 1 else 50 if ordinal == 1 else 0
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

        # Generar archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label='Descargar resultados en Excel',
            data=output,
            file_name='datos_lote_ejemplo.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

