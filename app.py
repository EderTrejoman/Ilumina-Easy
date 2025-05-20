import streamlit as st
import re
import math
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + IES", layout="centered")
st.title("🔆 Calculadora de Iluminación con archivo .IES")

uploaded_file = st.file_uploader("📥 Sube tu archivo .IES para extraer el flujo luminoso", type=["ies"])

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

flujo = extraer_flujo_luminoso(uploaded_file) if uploaded_file else None
if flujo:
    st.success(f"✅ Flujo luminoso extraído: {flujo} lm")
else:
    flujo = st.number_input("Flujo luminoso (lm)", min_value=0.0)

st.subheader("📐 Parámetros del recinto")
largo = st.number_input("Largo del recinto (m)", min_value=0.0)
ancho = st.number_input("Ancho del recinto (m)", min_value=0.0)
area = largo * ancho
st.markdown(f"**Área calculada automáticamente:** `{area:.2f} m²`")

h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0)
h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8)
h_efectiva = h_montaje - h_trabajo
rcr = 0
if h_efectiva > 0 and largo > 0 and ancho > 0:
    rcr = round(5 * (largo + ancho) / (largo * ancho) * h_efectiva, 2)
st.markdown(f"**Índice de Cavidad del Recinto (RCR):** `{rcr}`")

st.subheader("🎨 Reflectancias del recinto")
reflectancia_techo = st.number_input("Reflectancia del techo (ρcc)", min_value=0.0, max_value=1.0, value=0.7)
reflectancia_paredes = st.number_input("Reflectancia de las paredes (ρpp)", min_value=0.0, max_value=1.0, value=0.5)
reflectancia_piso = st.number_input("Reflectancia del piso (ρcf)", min_value=0.0, max_value=1.0, value=0.2)

cu = 0.6 * ((reflectancia_techo + reflectancia_paredes + reflectancia_piso)/3) * (1 / (1 + math.exp(-rcr + 3)))
cu = round(min(max(cu, 0.01), 1.0), 3)
st.markdown(f"**CU estimado automáticamente:** `{cu}`")

niveles_nom = {
    "Oficinas (actividades de lectura/escritura)": 300,
    "Áreas de tránsito o exteriores": 100,
    "Áreas técnicas o talleres": 500,
    "Laboratorios": 750,
    "Áreas de almacenamiento": 200,
    "Salas de cómputo": 300,
    "Salas de juntas": 200,
    "Pasillos y accesos": 100,
    "Zonas de descanso": 150
}

opcion = st.selectbox("Selecciona el tipo de área (según NOM-025)", list(niveles_nom.keys()))
lux_requerido = niveles_nom[opcion]
st.markdown(f"**Nivel de iluminancia requerido (lux):** `{lux_requerido}`")

ambiente = st.selectbox("Selecciona el tipo de ambiente", ["Limpio", "Sujeto a polvo o suciedad", "Ambiente industrial o agresivo"])
fm_dict = {
    "Limpio": 0.8,
    "Sujeto a polvo o suciedad": 0.7,
    "Ambiente industrial o agresivo": 0.6
}
fm = fm_dict[ambiente]
st.markdown(f"**Factor de mantenimiento (FM):** `{fm}`")

st.subheader("📊 Resultado")
if flujo > 0 and area > 0 and lux_requerido > 0:
    luminarias = math.ceil((area * lux_requerido) / (flujo * cu * fm))
    st.success(f"🔧 Número de luminarias necesarias: {luminarias}")

    cols = math.ceil(math.sqrt(luminarias * (largo / ancho)))
    rows = math.ceil(luminarias / cols)
    st.markdown("### 🖼️ Distribución estimada de luminarias")
    fig, ax = plt.subplots(figsize=(6, 6))
    for i in range(rows):
        for j in range(cols):
            if i * cols + j < luminarias:
                ax.plot(j + 0.5, i + 0.5, 'o', color='orange')
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Vista superior de la distribución estimada")
    st.pyplot(fig)
else:
    st.info("Introduce todos los datos para calcular el número de luminarias.")

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

**Tabla de factor de mantenimiento (FM) extendida:**

| Tipo de Ambiente                   | FM sugerido |
|------------------------------------|-------------|
| Limpio (oficinas, laboratorios)    | 0.8         |
| Polvoriento o uso moderado         | 0.7         |
| Industria ligera/agresiva          | 0.6         |
| Poco mantenimiento o corrosivo     | 0.5         |
""")

st.subheader("🌐 Enlaces de referencia externa")
st.markdown("""
- [📄 Tabla de factor de mantenimiento - La Pantalla](https://www.la-pantalla.com.ar/tabla-de-factor-de-mantenimiento-iluminacion/)
- [📘 NOM-025-STPS-2008 - Diario Oficial de la Federación](https://www.dof.gob.mx/normasOficiales/3275/stps/stps.htm)
- [📊 Manual Conelec (PDF)](https://kupdf.net/download/manuel-electrico-conelecpdf_5964e7bcdc0d6051532be324_pdf)
""")
import streamlit as st
import re
import math
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + IES", layout="centered")
st.title("🔆 Calculadora de Iluminación con archivo .IES")

uploaded_file = st.file_uploader("📥 Sube tu archivo .IES para extraer el flujo luminoso", type=["ies"])

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

flujo = extraer_flujo_luminoso(uploaded_file) if uploaded_file else None
if flujo:
    st.success(f"✅ Flujo luminoso extraído: {flujo} lm")
else:
    flujo = st.number_input("Flujo luminoso (lm)", min_value=0.0)

st.subheader("📐 Parámetros del recinto")
largo = st.number_input("Largo del recinto (m)", min_value=0.0)
ancho = st.number_input("Ancho del recinto (m)", min_value=0.0)
area = largo * ancho
st.markdown(f"**Área calculada automáticamente:** `{area:.2f} m²`")

h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0)
h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8)
h_efectiva = h_montaje - h_trabajo
rcr = 0
if h_efectiva > 0 and largo > 0 and ancho > 0:
    rcr = round(5 * (largo + ancho) / (largo * ancho) * h_efectiva, 2)
st.markdown(f"**Índice de Cavidad del Recinto (RCR):** `{rcr}`")

st.subheader("🎨 Reflectancias del recinto")
reflectancia_techo = st.number_input("Reflectancia del techo (ρcc)", min_value=0.0, max_value=1.0, value=0.7)
reflectancia_paredes = st.number_input("Reflectancia de las paredes (ρpp)", min_value=0.0, max_value=1.0, value=0.5)
reflectancia_piso = st.number_input("Reflectancia del piso (ρcf)", min_value=0.0, max_value=1.0, value=0.2)

cu = 0.6 * ((reflectancia_techo + reflectancia_paredes + reflectancia_piso)/3) * (1 / (1 + math.exp(-rcr + 3)))
cu = round(min(max(cu, 0.01), 1.0), 3)
st.markdown(f"**CU estimado automáticamente:** `{cu}`")

niveles_nom = {
    "Oficinas (actividades de lectura/escritura)": 300,
    "Áreas de tránsito o exteriores": 100,
    "Áreas técnicas o talleres": 500,
    "Laboratorios": 750,
    "Áreas de almacenamiento": 200,
    "Salas de cómputo": 300,
    "Salas de juntas": 200,
    "Pasillos y accesos": 100,
    "Zonas de descanso": 150
}

opcion = st.selectbox("Selecciona el tipo de área (según NOM-025)", list(niveles_nom.keys()))
lux_requerido = niveles_nom[opcion]
st.markdown(f"**Nivel de iluminancia requerido (lux):** `{lux_requerido}`")

ambiente = st.selectbox("Selecciona el tipo de ambiente", ["Limpio", "Sujeto a polvo o suciedad", "Ambiente industrial o agresivo"])
fm_dict = {
    "Limpio": 0.8,
    "Sujeto a polvo o suciedad": 0.7,
    "Ambiente industrial o agresivo": 0.6
}
fm = fm_dict[ambiente]
st.markdown(f"**Factor de mantenimiento (FM):** `{fm}`")

st.subheader("📊 Resultado")
if flujo > 0 and area > 0 and lux_requerido > 0:
    luminarias = math.ceil((area * lux_requerido) / (flujo * cu * fm))
    st.success(f"🔧 Número de luminarias necesarias: {luminarias}")

    cols = math.ceil(math.sqrt(luminarias * (largo / ancho)))
    rows = math.ceil(luminarias / cols)
    st.markdown("### 🖼️ Distribución estimada de luminarias")
    fig, ax = plt.subplots(figsize=(6, 6))
    for i in range(rows):
        for j in range(cols):
            if i * cols + j < luminarias:
                ax.plot(j + 0.5, i + 0.5, 'o', color='orange')
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Vista superior de la distribución estimada")
    st.pyplot(fig)
else:
    st.info("Introduce todos los datos para calcular el número de luminarias.")

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

**Tabla de factor de mantenimiento (FM) extendida:**

| Tipo de Ambiente                   | FM sugerido |
|------------------------------------|-------------|
| Limpio (oficinas, laboratorios)    | 0.8         |
| Polvoriento o uso moderado         | 0.7         |
| Industria ligera/agresiva          | 0.6         |
| Poco mantenimiento o corrosivo     | 0.5         |
""")

st.subheader("🌐 Enlaces de referencia externa")
st.markdown("""
- [📄 Tabla de factor de mantenimiento - La Pantalla](https://www.la-pantalla.com.ar/tabla-de-factor-de-mantenimiento-iluminacion/)
- [📘 NOM-025-STPS-2008 - Diario Oficial de la Federación](https://www.dof.gob.mx/normasOficiales/3275/stps/stps.htm)
- [📊 Manual Conelec (PDF)](https://kupdf.net/download/manuel-electrico-conelecpdf_5964e7bcdc0d6051532be324_pdf)
""")
