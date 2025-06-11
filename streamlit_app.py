import streamlit as st
import pandas as pd
import numpy as np
import io

st.markdown("<h1 style='text-align: center; color: white;'>Universidad Católica de Cuyo</h1>", unsafe_allow_html=True)
st.title("Calculadora de Exclusión Digital y Movilidad Social")

modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

if modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo_consolidado = st.file_uploader('Subí el archivo consolidado (.xlsx)', type='xlsx')
    
    if archivo_consolidado:
        try:
            df = pd.read_excel(archivo_consolidado)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # Mapeo de variables TIC
            if 'ip_iii_04' in df.columns:
                df['acceso_computadora'] = df['ip_iii_04'].map({1: 'Sí', 2: 'No'})
            if 'ip_iii_05' in df.columns:
                df['acceso_internet'] = df['ip_iii_05'].map({1: 'Sí', 2: 'No'})
            if 'ip_iii_06' in df.columns:
                df['capacitacion_tic'] = df['ip_iii_06'].map({1: 'Sí', 2: 'No'})

            # Intentar encontrar nivel_ed
            nivel_ed_col = next((col for col in df.columns if 'nivel_ed' in col.lower()), None)
            if nivel_ed_col:
                mapeo_nivel_ed = {
                    1: 'Sin instrucción',
                    2: 'Primario incompleto',
                    3: 'Primario completo',
                    4: 'Secundario incompleto',
                    5: 'Secundario completo',
                    6: 'Superior universitario incompleto',
                    7: 'Superior universitario completo'
                }
                df['nivel_educativo'] = df[nivel_ed_col].map(mapeo_nivel_ed)
            else:
                st.warning("No se encontró la columna 'nivel_ed'. Se asignará 0 por defecto a vulnerabilidad de movilidad social.")

            def calcular_indices(row):
                sub_acceso_computadora = 1 if row.get('acceso_computadora') == 'Sí' else 0
                sub_acceso_internet = 1 if row.get('acceso_internet') == 'Sí' else 0
                sub_capacitacion_tic = 1 if row.get('capacitacion_tic') == 'Sí' else 0
                sub_total = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic

                indice_ordinal = ((sub_total) / 3 * 90) + 10
                indice_binario = 1 if sub_total == 0 else 0
                vulnerabilidad_digital = ((3 - sub_total) / 3 * 90) + 10

                # Vulnerabilidad de Movilidad Social
                if 'nivel_educativo' in row and pd.notnull(row['nivel_educativo']):
                    puntaje_nivel_ed = {
                        'Sin instrucción': 7,
                        'Primario incompleto': 6,
                        'Primario completo': 5,
                        'Secundario incompleto': 4,
                        'Secundario completo': 3,
                        'Superior universitario incompleto': 2,
                        'Superior universitario completo': 1
                    }.get(row['nivel_educativo'], 0)
                    vulnerabilidad_educativa = (puntaje_nivel_ed / 7) * 50
                    vulnerabilidad_tic = 50 if row.get('capacitacion_tic') == 'No' else 0
                    vulnerabilidad_movilidad = vulnerabilidad_educativa + vulnerabilidad_tic
                    vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)
                else:
                    vulnerabilidad_movilidad = 0  # Valor por defecto si no hay nivel educativo

                return pd.Series([
                    indice_binario, indice_ordinal, vulnerabilidad_digital, vulnerabilidad_movilidad
                ], index=[
                    'indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad'
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

