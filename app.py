import streamlit as st
import re
import math
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + IES", layout="centered")
st.title("🔆 Calculadora de Iluminación con archivo .IES")

# --- INTRODUCCIÓN Y DEFINICIONES ---
# (Texto introductorio y tablas explicativas omitidos por brevedad)

# --- CARGA DE ARCHIVO IES ---
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

# --- PARÁMETROS DEL RECINTO ---
st.subheader("📐 Parámetros del recinto")
largo = st.number_input("Largo del recinto (m)", min_value=0.0)
ancho = st.number_input("Ancho del recinto (m)", min_value=0.0)
area = largo * ancho
st.markdown(f"**Área calculada automáticamente:** `{area:.2f} m²`")

col1, col2 = st.columns(2)
with col1:
    h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0)
with col2:
    h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8)

h_efectiva = h_montaje - h_trabajo
rcr = 0
if h_efectiva > 0 and largo > 0 and ancho > 0:
    rcr = round(5 * (largo + ancho) / (largo * ancho) * h_efectiva, 2)
st.markdown(f"**Índice de Cavidad del Recinto (RCR):** `{rcr}`")

st.subheader("🎨 Reflectancias del recinto")
ρcc = st.number_input("Reflectancia del techo (ρcc)", min_value=0.0, max_value=1.0, value=0.7)
ρpp = st.number_input("Reflectancia de las paredes (ρpp)", min_value=0.0, max_value=1.0, value=0.5)
ρcf = st.number_input("Reflectancia del piso (ρcf)", min_value=0.0, max_value=1.0, value=0.3)

cu = 0.6 * ((ρcc + ρpp + ρcf)/3) * (1 / (1 + math.exp(-rcr + 3)))
cu = round(min(max(cu, 0.01), 1.0), 3)
st.markdown(f"**CU estimado automáticamente:** `{cu}`")

st.subheader("🏢 Tipo de área (según NOM-025)")
areas = {
    "Áreas de trabajo en oficinas": 300,
    "Talleres y laboratorios": 500,
    "Salas de cómputo": 300,
    "Salas de juntas": 200,
    "Pasillos y accesos": 100,
    "Áreas de almacenamiento": 200,
    "Zonas de descanso": 150,
    "Áreas exteriores": 50
}
area_seleccionada = st.selectbox("Selecciona el tipo de área", list(areas.keys()))
lux_requerido = areas[area_seleccionada]
st.markdown(f"**Nivel de iluminancia requerido:** `{lux_requerido} lux`")

st.subheader("🏭 Ambiente de operación")
opciones_fm = {
    "🟢 Limpio": 0.8,
    "🟡 Moderado": 0.7,
    "🟠 Industrial ligero": 0.6,
    "🔴 Severo": 0.5
}
ambiente = st.selectbox("Selecciona el ambiente de operación", list(opciones_fm.keys()))
fm = opciones_fm[ambiente]
st.markdown(f"**FM aplicado automáticamente:** `{fm}`")

# --- CÁLCULO DIRECTO ---
st.subheader("💡 Cálculo estándar (de lux a luminarias)")
if flujo > 0 and cu > 0 and fm > 0:
    n_luminarias = math.ceil((area * lux_requerido) / (flujo * cu * fm))
    st.success(f"🔧 Número estimado de luminarias: {n_luminarias}")
else:
    st.warning("⚠️ Faltan datos para calcular el número de luminarias.")

# --- DISTRIBUCIÓN VISUAL ---
st.subheader("🖼️ Distribución estimada de luminarias")
if flujo > 0 and cu > 0 and fm > 0 and n_usuario > 0:
    cols = math.ceil(math.sqrt(n_usuario * (largo / ancho)))
    rows = math.ceil(n_usuario / cols)
    fig, ax = plt.subplots(figsize=(6, 6))
    for i in range(rows):
        for j in range(cols):
            if i * cols + j < n_usuario:
                ax.plot(j + 0.5, i + 0.5, 'o', color='orange')
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Vista superior del recinto con distribución estimada")
    st.pyplot(fig)

# --- CÁLCULO INVERSO ---
st.subheader("🔁 Modo inverso: ¿Qué lux obtengo con X luminarias?")
n_usuario = st.number_input("Número de luminarias disponibles", min_value=1, step=1)
if flujo > 0 and cu > 0 and fm > 0:
    lux_estimado = round((n_usuario * flujo * cu * fm) / area, 2)
    st.info(f"Con `{n_usuario}` luminarias de `{flujo} lm` se obtienen aproximadamente **{lux_estimado} lux**.")
    if lux_estimado < lux_requerido:
        st.error(f"❌ Advertencia: el nivel de iluminancia obtenido ({lux_estimado} lux) es inferior al requerido por la NOM-025 ({lux_requerido} lux).")
    elif lux_estimado >= lux_requerido:
        st.success("✅ Cumple con el nivel mínimo de iluminancia requerido.")
else:
    st.warning("⚠️ Ingresa todos los valores anteriores para estimar los lux.")
