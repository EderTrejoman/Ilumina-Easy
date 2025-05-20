import streamlit as st
import re
import math

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + IES", layout="centered")
st.title("🔆 Calculadora de Iluminación con archivo .IES")

st.markdown("""
Esta app te permite calcular el número de luminarias necesarias según la **NOM-025-STPS-2008**, utilizando flujo luminoso extraído automáticamente desde un archivo `.IES` o ingresado manualmente.
También incluye el cálculo del **RCR (Índice de Cavidad del Recinto)** y el ingreso manual del **CU**.
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
        return numeros[8]
    except:
        return None

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

# Parámetros físicos
st.subheader("📐 Parámetros del recinto")
largo = st.number_input("Largo del recinto (m)", min_value=0.0)
ancho = st.number_input("Ancho del recinto (m)", min_value=0.0)
area = largo * ancho
st.markdown(f"**Área calculada automáticamente:** `{area:.2f} m²`")

altura_total = st.number_input("Altura del recinto (m)", min_value=0.0)
h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0)
h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8)

# Cálculo del RCR
h_efectiva = altura_total - h_montaje - h_trabajo
rcr = 0
if h_efectiva > 0 and largo > 0 and ancho > 0:
    rcr = round(5 * (largo + ancho) / (largo * ancho) * h_efectiva, 2)
st.markdown(f"**Índice de Cavidad del Recinto (RCR):** `{rcr}`")

# Reflectancias
st.subheader("🎨 Reflectancias del recinto")
reflectancia_techo = st.selectbox("Reflectancia del techo (ρcc)", [0.2, 0.5, 0.7, 0.8], index=2)
reflectancia_paredes = st.selectbox("Reflectancia de las paredes (ρpp)", [0.2, 0.5, 0.7, 0.8], index=1)
reflectancia_piso = st.selectbox("Reflectancia del piso (ρcf)", [0.1, 0.2, 0.3, 0.4], index=1)

# CU manual
st.subheader("🔢 Parámetros de cálculo")
cu = st.number_input("Coeficiente de Utilización (CU)", min_value=0.01, max_value=1.0, value=0.6)
lux_requerido = st.number_input("Nivel de iluminancia requerido (lux)", min_value=0.0, value=300.0)
fm = st.number_input("Factor de Mantenimiento (FM)", min_value=0.01, max_value=1.0, value=0.8)

# Cálculo
st.subheader("📊 Resultado")
if flujo > 0 and area > 0 and lux_requerido > 0:
    luminarias = math.ceil((area * lux_requerido) / (flujo * cu * fm))
    st.success(f"🔧 Número de luminarias necesarias: {luminarias}")
else:
    st.info("Introduce todos los datos para calcular el número de luminarias.")

# Tablas de apoyo visual para el maestro
st.subheader("📚 Tablas de apoyo (según método cavidad zonal)")
st.markdown("""
**Tabla de reflectancias típicas:**

| Superficie | Acabado              | Reflectancia |
|------------|-----------------------|--------------|
| Techo      | Blanco / muy claro    | 0.7          |
| Techo      | Claro                 | 0.5          |
| Techo      | Medio                 | 0.3          |
| Paredes    | Claro                 | 0.5          |
| Paredes    | Medio                 | 0.3          |
| Paredes    | Oscuro                | 0.1          |
| Suelo      | Claro                 | 0.3          |
| Suelo      | Oscuro                | 0.1          |

**Tabla de factor de mantenimiento (FM):**

| Ambiente | FM recomendado |
|----------|----------------|
| Limpio   | 0.8            |
| Sucio    | 0.6            |
""")
