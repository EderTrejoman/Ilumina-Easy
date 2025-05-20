import streamlit as st
import re

st.set_page_config(page_title="Carga de IES - Flujo Luminoso", layout="centered")
st.title("📥 Carga de archivo .IES")
st.markdown("""
Este módulo te permite subir un archivo `.IES` y extraer automáticamente el **flujo luminoso total**.
Si el archivo no lo contiene, puedes ingresar el valor manualmente.
""")

uploaded_file = st.file_uploader("Carga tu archivo .IES para extraer el flujo luminoso", type=["ies"])

# Función para extraer flujo luminoso desde el .IES
def extraer_flujo_luminoso(archivo):
    contenido = archivo.read().decode("latin1").splitlines()
    for linea in contenido:
        if "LUMEN" in linea.upper() or "_TOTALLUMINAIRELUMENS" in linea.upper():
            valores = re.findall(r'\d+\.?\d*', linea)
            if valores:
                return float(valores[0])
    texto_completo = " ".join(contenido)
    numeros = re.findall(r'\d+\.?\d*', texto_completo)
    numeros = list(map(float, numeros))
    try:
        return numeros[8]  # Típicamente por la novena posición
    except:
        return None

# Entrada y validación
definir_flujo = None
if uploaded_file:
    flujo = extraer_flujo_luminoso(uploaded_file)
    if flujo:
        st.success(f"\u2705 Flujo luminoso total extraído: **{flujo} lúmenes**")
        definir_flujo = flujo
    else:
        st.warning("\u26A0\ufe0f No se pudo extraer el flujo luminoso del archivo. Ingrésalo manualmente.")
        definir_flujo = st.number_input("Introduce el flujo manualmente (lm)", min_value=0.0)
else:
    definir_flujo = st.number_input("Introduce el flujo manualmente (lm)", min_value=0.0)

# Resultado final
if definir_flujo:
    st.markdown(f"### \\n    **Flujo luminoso activo para cálculo:** `{definir_flujo} lm`")
    # Aquí puedes conectar el flujo con el cálculo de número de luminarias, lux, etc.