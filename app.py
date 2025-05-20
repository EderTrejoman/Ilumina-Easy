import streamlit as st
import re
import math

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + IES", layout="centered")
st.title("🔆 Calculadora de Iluminación con archivo .IES")

st.markdown("""
Esta app te permite calcular el número de luminarias necesarias según la **NOM-025-STPS-2008**, utilizando flujo luminoso extraído automáticamente desde un archivo `.IES` o ingresado manualmente.
También incluye el cálculo del **RCR (Índice de Cavidad del Recinto)** a partir de las alturas del plano de trabajo y montaje.
""")

uploaded_file = st.file_uploader("📥 Sube tu archivo .IES para extraer el flujo luminoso", type=["ies"])

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

# Entrada de flujo luminoso
flujo = None
if uploaded_file:
    flujo_extraido = extraer_flujo_luminoso(uploaded_file)
    if flujo_extraido:
        st.success(f"✅ Flujo luminoso extraído: {flujo_extraido} lm")
        flujo = flujo_extraido
    else:
        st.warning("⚠️ No se pudo extraer el flujo. Introduce manualmente:")
        flujo = st.number_input("Flujo luminoso (lm)", min_value=0.0)
else:
    flujo = st.number_input("Flujo luminoso (lm)", min_value=0.0)

# Entradas para parámetros del recinto
st.subheader("📐 Parámetros del recinto")
area = st.number_input("Área del recinto (m²)", min_value=0.0)
largo = st.number_input("Largo del recinto (m)", min_value=0.0)
ancho = st.number_input("Ancho del recinto (m)", min_value=0.0)
altura_total = st.number_input("Altura del recinto (m)", min_value=0.0)
h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0)
h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8)

# Cálculo de RCR
h_efectiva = altura_total - h_montaje - h_trabajo
if h_efectiva <= 0:
    rcr = 0
else:
    rcr = 5 * (largo + ancho) / (largo * ancho) * h_efectiva
st.markdown(f"**Índice de Cavidad del Recinto (RCR):** `{rcr:.2f}`")

# Parámetros fotométricos
lux_requerido = st.number_input("Nivel de iluminancia requerido (lux)", min_value=0.0, value=300.0)
cu = st.number_input("Coeficiente de Utilización (CU)", min_value=0.01, max_value=1.0, value=0.6)
fm = st.number_input("Factor de Mantenimiento (FM)", min_value=0.01, max_value=1.0, value=0.8)

# Cálculo de número de luminarias
st.subheader("🔢 Resultado")
if flujo > 0 and area > 0 and lux_requerido > 0:
    luminarias = math.ceil((area * lux_requerido) / (flujo * cu * fm))
    st.success(f"🔧 Número de luminarias necesarias: {luminarias}")
else:
    st.info("Introduce todos los datos para calcular el número de luminarias.")
