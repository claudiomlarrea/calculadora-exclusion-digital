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
- **Porcentaje de Vulnerabilidad de Movilidad Social (%):** Calcula el riesgo de movilidad social reducida (10%-100%).
""", unsafe_allow_html=True)

modo = st.radio('Seleccioná el modo de uso:', ['Ingreso individual', 'Carga por lote (Excel)'])

# -----------------------------------------------
# Modo de carga por lote (Excel)
if modo == 'Carga por lote (Excel)':
    st.header('Carga de Datos por Lote')
    archivo_consolidado = st.file_uploader('Subí el archivo consolidado (.xlsx) del 4º trimestre', type='xlsx')

    if archivo_consolidado:
        try:
            df = pd.read_excel(archivo_consolidado)

            # Limpiar y estandarizar nombres de columnas
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            st.success("Archivo consolidado cargado correctamente.")

            # Mapear nivel educativo
            mapeo_nivel_ed = {
                1: 'Sin instrucción',
                2: 'Primario incompleto',
                3: 'Primario completo',
                4: 'Secundario incompleto',
                5: 'Secundario completo',
                6: 'Superior universitario incompleto',
                7: 'Superior universitario completo',
                8: 'Universitario incompleto',
                9: 'Universitario completo'
            }

            if 'nivel_ed' in df.columns:
                df['nivel_educativo'] = df['nivel_ed'].map(mapeo_nivel_ed)
            else:
                st.warning("La columna 'nivel_ed' no se encuentra en el archivo.")

            # Mapear variables TIC
            if 'ip_iii_04' in df.columns:
                df['acceso_computadora'] = df['ip_iii_04'].map({1: 'Sí', 2: 'No'})
            if 'ip_iii_05' in df.columns:
                df['acceso_internet'] = df['ip_iii_05'].map({1: 'Sí', 2: 'No'})
            if 'ip_iii_06' in df.columns:
                df['capacitacion_tic'] = df['ip_iii_06'].map({1: 'Sí', 2: 'No'})

            # Mapear región
            mapeo_region = {
                1: 'Gran Buenos Aires',
                2: 'Pampeana',
                3: 'Noroeste',
                4: 'Noreste',
                5: 'Cuyo',
                6: 'Patagonia'
            }
            if 'region' in df.columns:
                df['region'] = df['region'].map(mapeo_region)

            # Calcular índices
            def calcular_indices(row):
                sub_acceso_computadora = 1 if row.get('acceso_computadora') == 'Sí' else 0
                sub_acceso_internet = 1 if row.get('acceso_internet') == 'Sí' else 0
                sub_capacitacion_tic = 1 if row.get('capacitacion_tic') == 'Sí' else 0

                sub_total = sub_acceso_computadora + sub_acceso_internet + sub_capacitacion_tic
                indice_ordinal = ((sub_total) / 3 * 90) + 10
                indice_binario = 1 if sub_total == 0 else 0
                vulnerabilidad_digital = ((3 - sub_total) / 3 * 90) + 10

                vulnerabilidad_movilidad = 10
                if row.get('nivel_educativo') in ['Sin instrucción', 'Primario incompleto']:
                    vulnerabilidad_movilidad += 45
                if row.get('capacitacion_tic') == 'No':
                    vulnerabilidad_movilidad += 45
                vulnerabilidad_movilidad = min(vulnerabilidad_movilidad, 100)

                return pd.Series([
                    indice_binario, indice_ordinal,
                    vulnerabilidad_digital, vulnerabilidad_movilidad
                ], index=[
                    'indice_binario', 'indice_ordinal',
                    'vulnerabilidad_digital', 'vulnerabilidad_movilidad'
                ])

            df[['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']] = df.apply(calcular_indices, axis=1)

            for col in ['indice_binario', 'indice_ordinal', 'vulnerabilidad_digital', 'vulnerabilidad_movilidad']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            st.success('Datos procesados correctamente')
            st.dataframe(df)

            st.markdown("""
---
### 📌 Extracto de los índices calculados:
- **Índice Binario de Exclusión Digital:** 1 si la persona está completamente excluida digitalmente; 0 en caso contrario.
- **Índice Ordinal de Exclusión Digital (%):** Expresa el nivel de acceso digital en porcentaje (10%-100%).
- **Porcentaje de Vulnerabilidad Digital (%):** Cuantifica la exclusión digital en escala de 10%-100%.
- **Porcentaje de Vulnerabilidad de Movilidad Social (%):** Calcula el riesgo de movilidad social reducida (10%-100%).
""")

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

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")





