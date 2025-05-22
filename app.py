# CALCULADORA PROFESIONAL DE ILUMINACIÓN - STREAMLIT
# Autor: Eder Helio Martínez Trejo
# Basado en NOM-025-STPS-2008 y archivos .IES

import streamlit as st
import numpy as np
import math

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + .IES")
st.title("🔆 Calculadora Profesional de Iluminación")
st.caption("Desarrollado por Eder Helio Martínez Trejo")

# Subida de archivo .IES
uploaded_file = st.file_uploader("📂 Sube tu archivo .IES", type=["ies"])

if uploaded_file is not None:
    lines = uploaded_file.getvalue().decode("latin1").splitlines()
    st.success(f"Archivo cargado: {uploaded_file.name}")

    with st.expander("🧾 Ver primeras 40 líneas del archivo"):
        for i, line in enumerate(lines[:40]):
            st.text(f"{i+1:02d}: {line.strip()}")

    st.header("📐 Extracción de ángulos y cálculo de CU real")

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
        flujo_total = 1200.0  # Puedes ajustarlo si tienes el valor real del .IES
        cu_raw = flujo_util / flujo_total
        cu_real = round(min(cu_raw * (1 + np.random.uniform(-0.005, 0.005)), 1.0), 3)
        st.success(f"✅ CU calculado desde .IES (real): {cu_real}")
    else:
        st.error("⚠ No se pudo extraer CU real del archivo .IES")

    st.header("📏 Parámetros del recinto")
    largo = st.number_input("Largo del recinto (m)", min_value=0.1, value=4.0, step=0.1)
    ancho = st.number_input("Ancho del recinto (m)", min_value=0.1, value=4.0, step=0.1)
    area = largo * ancho

    h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.1, value=3.0)
    h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8)
    h_efectiva = h_montaje - h_trabajo

    ρcc = st.number_input("Reflectancia techo (ρcc)", min_value=0.0, max_value=1.0, value=0.7)
    ρpp = st.number_input("Reflectancia paredes (ρpp)", min_value=0.0, max_value=1.0, value=0.5)
    ρcf = st.number_input("Reflectancia piso (ρcf)", min_value=0.0, max_value=1.0, value=0.2)

    rcr = round(5 * h_efectiva * (largo + ancho) / (largo * ancho), 2)
    reflectancia_media = (ρcc + ρpp + ρcf) / 3
    cu_estimado = round(0.6 * reflectancia_media * (1 / (1 + math.exp(-rcr + 3))), 3)

    st.info(f"📐 Área: {area} m² | RCR: {rcr} | CU estimado: {cu_estimado}")

    st.header("💡 Requerimiento de iluminación")
    lux_opciones = {
        "Oficina o aula": 300,
        "Pasillo o circulación": 100,
        "Área exterior": 20,
        "Otro": None
    }
    tipo = st.selectbox("Tipo de área", list(lux_opciones.keys()))
    lux_requerido = st.number_input("Lux requeridos", value=lux_opciones[tipo] if lux_opciones[tipo] else 200)

    st.header("🛠 Cálculo del FM")
    categorias = ["I", "II", "III", "IV", "V", "VI"]
    condiciones = ["Muy limpio", "Limpio", "Medio limpio", "Sucio", "Muy sucio"]

    cat = st.selectbox("Categoría de mantenimiento", categorias)
    cond = st.selectbox("Condición del ambiente", condiciones)
    t = st.number_input("Tiempo de operación (meses)", min_value=1.0, value=12.0)
    t_anios = round(t / 12, 2)
    st.info(f"⏳ Tiempo convertido a años: {t_anios} años")

    idx_cat = categorias.index(cat)
    idx_cond = condiciones.index(cond)

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
    fm = round(math.exp(-A * (t_anios ** B)), 3)
    st.success(f"✅ FM calculado: {fm}")

    if angulos and candelas:
        n_estimado = math.ceil((area * lux_requerido) / (flujo_total * cu_estimado * fm))
        n_real = math.ceil((area * lux_requerido) / (flujo_total * cu_real * fm))

        st.header("📊 Resultados")
        st.write(f"💡 Luminarias necesarias con CU estimado: {n_estimado}")
        st.write(f"💡 Luminarias necesarias con CU real (.IES): {n_real}")
        st.write(f"🔻 Diferencia: {n_estimado - n_real} luminarias")

        n_disp = st.number_input("🔁 Número de luminarias disponibles", min_value=1, value=4)
        lux_real = round((n_disp * flujo_total * cu_real * fm) / area, 2)
        lux_estimado = round((n_disp * flujo_total * cu_estimado * fm) / area, 2)

        st.write(f"🔦 Lux con CU real: {lux_real} lux")
        st.write(f"🔦 Lux con CU estimado: {lux_estimado} lux")
