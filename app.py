import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import io
import math

st.set_page_config(page_title="Calculadora de CU", page_icon="🔆", layout="centered")
st.title("🔆 Calculadora de Luminarias mediante archivos .IES")

st.markdown("""
## 📝 Introducción
El diseño de sistemas de iluminación eficientes y normativamente correctos es esencial en cualquier entorno laboral o educativo. Esta herramienta permite calcular el **Coeficiente de Utilización (CU)** a partir de archivos **.IES**, además de estimar el número de luminarias necesarias conforme a la **NOM-025-STPS-2008**. 


## 🎯 Objetivo
Brindar una herramienta práctica y precisa desarrollada por **alumnos de 8º semestre de Ingeniería Eléctrica del ITSH** para facilitar el diseño de sistemas de iluminación.
""")

st.markdown("### 📎 Suba un archivo .IES")
uploaded_file = st.file_uploader("", type="ies")

st.markdown("""
**ℹ️ Información para el usuario:**

- **Altura del plano de trabajo:** es la distancia desde el piso hasta la superficie donde se realiza la tarea visual (por ejemplo, un escritorio o mesa). Generalmente se asume **0.80 m** para oficinas o aulas.
- **Altura de montaje:** es la distancia desde el piso hasta el centro de la luminaria instalada en el techo.
- **Altura efectiva:** es la diferencia entre la altura de montaje y la altura del plano de trabajo, y representa la altura útil para el cálculo de iluminación.
""")

altura_montaje = st.number_input("Ingrese la altura de montaje en metros", min_value=0.0, value=2.5, step=0.1)
altura_trabajo = st.number_input("Ingrese la altura del plano de trabajo en metros", min_value=0.0, value=0.8, step=0.1)
altura_efectiva = altura_montaje - altura_trabajo
st.markdown(f"**Altura efectiva:** {altura_efectiva:.2f} m")

def leer_ies(file):
    lines = file.read().decode('latin1').splitlines()
    metadata = []
    data_lines = []
    for line in lines:
        if line.strip().startswith('TILT'):
            tilt_index = lines.index(line)
            metadata = lines[:tilt_index + 1]
            data_lines = lines[tilt_index + 1:]
            break

    header = data_lines[0].strip().split()
    flujo_total = float(header[1])
    num_ang_vert = int(header[3])
    num_ang_horiz = int(header[4])

    angulo_vert = list(map(float, data_lines[2].strip().split()))
    idx = 3
    while len(angulo_vert) < num_ang_vert:
        angulo_vert += list(map(float, data_lines[idx].strip().split()))
        idx += 1

    angulo_horiz = list(map(float, data_lines[idx].strip().split()))
    idx += 1
    while len(angulo_horiz) < num_ang_horiz:
        angulo_horiz += list(map(float, data_lines[idx].strip().split()))
        idx += 1

    candela_vals = []
    while idx < len(data_lines):
        line_vals = data_lines[idx].strip().split()
        if line_vals:
            candela_vals += list(map(float, line_vals))
        idx += 1

    expected_vals = num_ang_horiz * num_ang_vert
    if len(candela_vals) != expected_vals:
        st.warning(f"⚠️ Aviso: se esperaban {expected_vals} candelas, pero se encontraron {len(candela_vals)}")
        if len(candela_vals) % num_ang_vert == 0:
            num_ang_horiz = len(candela_vals) // num_ang_vert
            st.info(f"🔁 Ajustando número de planos horizontales a {num_ang_horiz}")
        elif len(candela_vals) % num_ang_horiz == 0:
            num_ang_vert = len(candela_vals) // num_ang_horiz
            st.info(f"🔁 Ajustando número de ángulos verticales a {num_ang_vert}")
        else:
            raise ValueError("La cantidad de candelas no coincide con los ángulos especificados.")

    C = np.array(candela_vals).reshape((num_ang_horiz, num_ang_vert))
    theta_vals = np.array(angulo_vert[:num_ang_vert])
    return C, theta_vals, flujo_total, num_ang_horiz, num_ang_vert

def calcular_cu(C, theta_vals, flujo_total):
    mask = theta_vals <= 90
    theta_rad = np.radians(theta_vals[mask])
    I_avg = np.mean(C, axis=0)[mask]
    flujo_util = np.trapz(I_avg * np.sin(theta_rad) * 2 * np.pi * np.cos(theta_rad), theta_rad)
    CU = flujo_util / flujo_total
    return CU, flujo_util

def calcular_fm(A, B, t):
    return np.exp(-A * (t ** B))

niveles_nom = {
    "Oficina": 300,
    "Aula": 300,
    "Pasillo": 100,
    "Almacén": 150,
    "Taller": 500,
    "Área exterior": 20,
    "Laboratorio": 750,
    "Sala de cómputo": 300
}

if uploaded_file is not None:
    try:
        C, theta, flujo_total, nh, nv = leer_ies(uploaded_file)
        cu, flujo_util = calcular_cu(C, theta, flujo_total)

        st.success("✅ Archivo procesado")
        st.markdown(f"- 📏 Ángulos verticales: {nv}")
        st.markdown(f"- 🧭 Planos horizontales: {nh}")
        st.markdown(f"- 🔸 Flujo útil: {round(flujo_util, 1)} lm")
        st.markdown(f"- 🔸 Flujo total: {flujo_total} lm")
        st.markdown(f"- 🔹 CU real calculado: {round(cu, 3)}")

        st.markdown("---")
        st.markdown("### 📐 Dimensiones del área a iluminar")

        largo = st.number_input("Largo del área (m)", min_value=0.0, value=6.0, step=0.1)
        ancho = st.number_input("Ancho del área (m)", min_value=0.0, value=6.0, step=0.1)
        area = largo * ancho
        st.markdown(f"**Área total:** {area:.2f} m²")

        tipo_area = st.selectbox("Seleccione el tipo de área según la NOM-025-STPS-2008", list(niveles_nom.keys()))
        nivel_lux = niveles_nom[tipo_area]
        st.markdown(f"**Nivel de iluminación requerido:** {nivel_lux} lux")

        st.markdown("---")
        st.markdown("### ⚙️ Parámetros de mantenimiento")

        tiempo_meses = st.number_input("Tiempo de operación (meses)", min_value=0.0, value=6.0, step=1.0)
        t = tiempo_meses / 12.0

        categorias = {
            "I": (0.301, 0.069),
            "II": (0.188, 0.062),
            "III": (0.147, 0.070),
            "IV": (0.103, 0.083),
            "V": (0.084, 0.088),
            "VI": (0.076, 0.088),
        }

        descripcion_categorias = {
            "I": "Nada",
            "II": "Transparente con ≥15% de luz hacia arriba",
            "III": "Transparente con <15% de luz hacia arriba",
            "IV": "Opaca con ≥15% de luz hacia arriba",
            "V": "Opaca con <15% de luz hacia arriba",
            "VI": "Opaca sin aberturas",
        }

        categoria = st.selectbox("Categoría de mantenimiento (superior)", list(categorias.keys()), format_func=lambda x: f"{x} - {descripcion_categorias[x]}")
        A, B = categorias[categoria]
        FM = calcular_fm(A, B, t)
        st.markdown(f"**Factor de mantenimiento (FM):** {FM:.3f}")

        num_luminarias = (nivel_lux * area) / (cu * flujo_total * FM)
        st.markdown(f"### 🔢 Luminarias necesarias: **{round(num_luminarias, 1)}**")

        st.markdown("---")
        st.markdown("### 📊 Niveles de Iluminación según la NOM-025-STPS-2008")
        st.dataframe({"Área": list(niveles_nom.keys()), "Nivel de Iluminación (lux)": list(niveles_nom.values())})

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo .IES: {e}")
