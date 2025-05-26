import numpy as np
import streamlit as st

st.set_page_config(page_title="Calculadora de CU", page_icon="🔆")
st.title("🔆 Calculadora de CU desde archivo .IES")

st.markdown("### 📎 Suba un archivo .IES")
uploaded_file = st.file_uploader("", type="ies")

st.markdown("""
*ℹ Información para el usuario:*

- *Altura del plano de trabajo (hrc):* distancia del piso a la superficie donde se realiza la tarea (ej. escritorio, mesa), normalmente *0.80 m*.
- *Altura de montaje (hcc):* distancia desde el piso hasta el centro de la luminaria instalada en el techo.
- *Altura efectiva (hfc):* diferencia entre hcc y hrc, representa la altura útil para los cálculos de iluminación.
""")

hcc = st.number_input("Altura de montaje (hcc) [m]", min_value=0.0, value=2.5, step=0.1)
hrc = st.number_input("Altura del plano de trabajo (hrc) [m]", min_value=0.0, value=0.8, step=0.1)
hfc = hcc - hrc
st.markdown(f"*Altura efectiva (hfc):* {hfc:.2f} m")

def leer_ies(file):
    lines = file.read().decode('latin1').splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("TILT"):
            data_lines = lines[i+1:]
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
        st.warning(f"⚠ Aviso: se esperaban {expected_vals} candelas, pero se encontraron {len(candela_vals)}")
        if len(candela_vals) % num_ang_vert == 0:
            num_ang_horiz = len(candela_vals) // num_ang_vert
        elif len(candela_vals) % num_ang_horiz == 0:
            num_ang_vert = len(candela_vals) // num_ang_horiz
        else:
            raise ValueError("Dimensiones incompatibles.")

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

if uploaded_file:
    try:
        C, theta, flujo_total, nh, nv = leer_ies(uploaded_file)
        cu, flujo_util = calcular_cu(C, theta, flujo_total)

        st.success("✅ Archivo procesado")
        st.markdown(f"- Ángulos verticales: {nv}")
        st.markdown(f"- Planos horizontales: {nh}")
        st.markdown(f"- Flujo útil: {round(flujo_util, 1)} lm")
        st.markdown(f"- Flujo total: {flujo_total} lm")
        st.markdown(f"- CU real calculado: *{round(cu, 3)}*")

        st.markdown("---")
        st.markdown("### 📐 Dimensiones del área a iluminar")

        largo = st.number_input("Largo del área (m)", min_value=0.0, value=6.0, step=0.1)
        ancho = st.number_input("Ancho del área (m)", min_value=0.0, value=6.0, step=0.1)
        area = largo * ancho
        st.markdown(f"*Área total:* {area:.2f} m²")

        nivel_lux = st.number_input("Nivel de iluminación requerido (lux)", min_value=0, value=300, step=10)
        FM = st.number_input("Factor de mantenimiento (FM)", min_value=0.1, max_value=1.0, value=0.9, step=0.05)

        num_luminarias = (nivel_lux * area) / (cu * flujo_total * FM)
        st.markdown(f"### 🔢 Luminarias necesarias: *{round(num_luminarias, 1)}*")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo .IES: {e}")
