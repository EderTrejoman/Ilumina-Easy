import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + .IES")
st.title("🔆 Calculadora de Iluminación")
st.caption("Autor: Eder Helio Martínez Trejo — Basado en NOM-025-STPS-2008 y archivos .IES")

uploaded_file = st.file_uploader("📂 Sube tu archivo .IES", type=["ies"])

if uploaded_file is not None:
    lines = uploaded_file.getvalue().decode("latin1").splitlines()
    st.success(f"Archivo cargado: {uploaded_file.name}")

    with st.expander("🧾 Ver primeras 40 líneas del archivo"):
        for i, line in enumerate(lines[:40]):
            st.text(f"{i+1:02d}: {line.strip()}")

    # Extracción de ángulos y candelas
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

    st.subheader("📏 Parámetros del recinto")
    largo = st.number_input("Largo del recinto (m)", value=4.0)
    ancho = st.number_input("Ancho del recinto (m)", value=4.0)
    h_montaje = st.number_input("Altura de montaje (m)", value=3.0)
    h_trabajo = st.number_input("Altura del plano de trabajo (m)", value=0.8)

    ρcc = st.number_input("Reflectancia techo (ρcc)", min_value=0.0, max_value=1.0, value=0.7)
    ρpp = st.number_input("Reflectancia paredes (ρpp)", min_value=0.0, max_value=1.0, value=0.5)
    ρcf = st.number_input("Reflectancia piso (ρcf)", min_value=0.0, max_value=1.0, value=0.2)

    area = largo * ancho
    h_efectiva = h_montaje - h_trabajo
    rcr = round(5 * h_efectiva * (largo + ancho) / (largo * ancho), 2)
    reflectancia_media = (ρcc + ρpp + ρcf) / 3
    cu_estimado = round(0.6 * reflectancia_media * (1 / (1 + math.exp(-rcr + 3))), 3)

    st.info(f"📐 RCR: {rcr} — CU estimado: {cu_estimado}")

    st.subheader("💡 Nivel de iluminancia requerido")
    tipo_area = st.selectbox("Tipo de área según NOM-025", ["Oficina / Aula (300 lux)", "Pasillo (100 lux)", "Exterior (20 lux)", "Otro (ingresar manual)"])
    if tipo_area == "Oficina / Aula (300 lux)":
        lux_requerido = 300
    elif tipo_area == "Pasillo (100 lux)":
        lux_requerido = 100
    elif tipo_area == "Exterior (20 lux)":
        lux_requerido = 20
    else:
        lux_requerido = st.number_input("Ingresa nivel de iluminancia (lux)", value=200)

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

    # Cálculo de luminarias
    n_estimado = math.ceil((area * lux_requerido) / (flujo_total * cu_estimado * fm))
    n_real = math.ceil((area * lux_requerido) / (flujo_total * cu_real * fm))

    st.subheader("🔢 Resultado: número de luminarias necesarias")
    st.write(f"💡 Con CU estimado: {n_estimado} luminarias")
    st.write(f"💡 Con CU real (.IES): {n_real} luminarias")
    st.write(f"🔻 Diferencia: {n_estimado - n_real} luminarias")

    st.subheader("🔁 Modo inverso: ¿qué lux logro con X luminarias?")
    n_usuario = st.number_input("Número de luminarias disponibles", min_value=1, value=4)

    lux_real = round((n_usuario * flujo_total * cu_real * fm) / area, 2)
    lux_estimado = round((n_usuario * flujo_total * cu_estimado * fm) / area, 2)

    st.write(f"🔦 Lux con CU real: {lux_real} lux")
    st.write(f"🔦 Lux con CU estimado: {lux_estimado} lux")

    if lux_real < lux_requerido:
        st.warning(f"⚠ CU real: por debajo del requerido ({lux_requerido} lux)")
    else:
        st.success("✅ CU real cumple el nivel de iluminancia.")

    if lux_estimado < lux_requerido:
        st.warning(f"⚠ CU estimado: por debajo del requerido ({lux_requerido} lux)")
    else:
        st.success("✅ CU estimado cumple el nivel de iluminancia.")

    st.subheader("📊 Visualización 2D de luminarias")
    n_x = st.number_input("Luminarias en eje X (largo)", min_value=1, value=2)
    n_y = st.number_input("Luminarias en eje Y (ancho)", min_value=1, value=2)

    x_spacing = largo / (n_x + 1)
    y_spacing = ancho / (n_y + 1)

    x_coords = [x_spacing * (j + 1) for j in range(n_x) for i in range(n_y)]
    y_coords = [y_spacing * (i + 1) for j in range(n_x) for i in range(n_y)]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(x_coords, y_coords, s=200, c="orange", edgecolors="black", label="Luminaria")
    ax.set_title("Distribución de luminarias en planta")
    ax.set_xlabel("Largo (m)")
    ax.set_ylabel("Ancho (m)")
    ax.set_xlim(0, largo)
    ax.set_ylim(0, ancho)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
