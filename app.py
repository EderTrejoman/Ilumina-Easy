# CALCULADORA DE ILUMINACION NOM-025-STPS-2008 + .IES
# Autor: Eder Helio Martínez Trejo

import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + .IES")
st.title("🔆 Calculadora Profesional de Iluminación")
st.caption("Desarrollado por Eder Helio Martínez Trejo")

# INTRODUCCIÓN Y OBJETIVO
st.markdown("""
### 🎯 Objetivo
Esta calculadora está diseñada para estimar de forma profesional el número de luminarias necesarias según la **NOM-025-STPS-2008**, considerando:
- El **CU real** extraído desde archivos `.IES`
- El **CU estimado** por reflectancias y RCR
- Las condiciones del recinto, mantenimiento y tipo de área

El objetivo es facilitar decisiones técnicas fundamentadas y visuales sobre eficiencia luminosa en espacios laborales.
""")

uploaded_file = st.file_uploader("📂 Sube tu archivo .IES", type=["ies"])

if uploaded_file is not None:
    lines = uploaded_file.getvalue().decode("latin1").splitlines()
    st.success(f"Archivo cargado: {uploaded_file.name}")

    with st.expander("🧾 Ver primeras 40 líneas del archivo"):
        for i, line in enumerate(lines[:40]):
            st.text(f"{i+1:02d}: {line.strip()}")

    # Extracción de CU desde .IES
    angulos = []
    candelas = []

    for line in lines:
        valores = line.strip().split()
        try:
            valores = [float(x) for x in valores]
        except:
            continue
        if len(valores) > 10:
            if not angulos:
                angulos = valores
            elif not candelas:
                candelas = valores
            if angulos and candelas:
                break

    if angulos and candelas:
        n = min(len(angulos), len(candelas))
        ang_rad = np.radians(angulos[:n])
        candelas_utiles = np.array(candelas[:n]) * np.sin(ang_rad) * 2 * np.pi * np.cos(ang_rad)
        flujo_util = np.trapz(candelas_utiles, ang_rad)
        flujo_total = st.number_input("🔢 Flujo total declarado por la luminaria (lm)", value=1200.0)
        cu_real = round(flujo_util / flujo_total, 3)
        st.success(f"✅ CU calculado desde .IES (real): {cu_real}")
    else:
        st.error("⚠ No se pudo extraer CU real. Asegúrate de que el archivo tenga ángulos y candelas.")

    # Dimensiones del recinto
    st.subheader("📏 Parámetros del recinto")

    largo = st.number_input("Largo del recinto (m)", min_value=0.0, max_value=200.0, value=4.0, step=0.01, format="%.2f")
    ancho = st.number_input("Ancho del recinto (m)", min_value=0.0, max_value=200.0, value=4.0, step=0.01, format="%.2f")
    h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0, max_value=200.0, value=3.0, step=0.01, format="%.2f")
    h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, max_value=200.0, value=0.8, step=0.01, format="%.2f")

    ρcc = st.number_input("Reflectancia techo (ρcc)", min_value=0.0, max_value=1.0, value=0.7)
    ρpp = st.number_input("Reflectancia paredes (ρpp)", min_value=0.0, max_value=1.0, value=0.5)
    ρcf = st.number_input("Reflectancia piso (ρcf)", min_value=0.0, max_value=1.0, value=0.2)

    area = largo * ancho
    h_efectiva = h_montaje - h_trabajo
    rcr = round(5 * h_efectiva * (largo + ancho) / (largo * ancho), 2)
    reflectancia_media = (ρcc + ρpp + ρcf) / 3
    cu_estimado = round(0.6 * reflectancia_media * (1 / (1 + math.exp(-rcr + 3))), 3)

    st.info(f"📐 RCR: {rcr} — CU estimado: {cu_estimado}")

    # Nivel de iluminancia
    st.subheader("💡 Nivel de iluminancia requerido")

    areas_nom = {
        "Oficina o aula": 300,
        "Pasillo o circulación": 100,
        "Área exterior": 20,
        "Archivo o biblioteca": 200,
        "Recepción": 150,
        "Escaleras": 150,
        "Área de producción detallada": 500,
        "Área de inspección o precisión": 750,
        "Otro (ingresar manual)": None
    }

    tipo_area = st.selectbox("Selecciona el tipo de área", list(areas_nom.keys()))
    if areas_nom[tipo_area] is None:
        lux_requerido = st.number_input("Ingresa iluminancia requerida (lux)", value=200.0)
    else:
        lux_requerido = areas_nom[tipo_area]

    # Factor de mantenimiento
    st.subheader("🛠 Cálculo del Factor de Mantenimiento (FM)")

    categorias = ["I", "II", "III", "IV", "V", "VI"]
    condiciones = ["Muy limpio", "Limpio", "Medio limpio", "Sucio", "Muy sucio"]

    categoria = st.selectbox("Categoría de mantenimiento", categorias)
    condicion = st.selectbox("Condición del ambiente", condiciones)
    t = st.number_input("Tiempo de operación (meses)", min_value=1.0, value=12.0)

    idx_cat = categorias.index(categoria)
    idx_cond = condiciones.index(condicion)

    tabla_B = [0.69, 0.62, 0.70, 0.72, 0.83, 0.88]
    tabla_A = [
        [0.038, 0.071, 0.111, 0.162, 0.301],
        [0.033, 0.068, 0.102, 0.147, 0.188],
        [0.079, 0.106, 0.143, 0.184, 0.236],
        [0.070, 0.131, 0.214, 0.314, 0.452],
        [0.078, 0.128, 0.190, 0.249, 0.321],
        [0.076, 0.145, 0.218, 0.284, 0.396]
    ]

    A = tabla_A[idx_cat][idx_cond]
    B = tabla_B[idx_cat]
    fm = round(math.exp(-A * (t ** B)), 3)
    st.success(f"✅ FM calculado: {fm}")
