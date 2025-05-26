import streamlit as st
import numpy as np

st.title("🔆 Calculadora de CU desde archivo .IES")

def leer_ies(nombre_archivo):
    lines = nombre_archivo.decode('latin1').splitlines()

    for i, line in enumerate(lines):
        if line.strip().startswith('TILT'):
            tilt_index = i
            break

    header = lines[tilt_index + 1].strip().split()
    flujo_total = float(header[1])
    num_ang_vert = int(header[3])
    num_ang_horiz = int(header[4])

    idx = tilt_index + 3
    angulo_vert = list(map(float, lines[idx].strip().split()))
    idx += 1
    while len(angulo_vert) < num_ang_vert:
        angulo_vert += list(map(float, lines[idx].strip().split()))
        idx += 1

    angulo_horiz = list(map(float, lines[idx].strip().split()))
    idx += 1
    while len(angulo_horiz) < num_ang_horiz:
        angulo_horiz += list(map(float, lines[idx].strip().split()))
        idx += 1

    candela_vals = []
    while idx < len(lines):
        vals = lines[idx].strip().split()
        if vals:
            candela_vals += list(map(float, vals))
        idx += 1

    expected_vals = num_ang_horiz * num_ang_vert
    if len(candela_vals) != expected_vals:
        st.warning(f"⚠️ Se esperaban {expected_vals} valores de candelas, pero se encontraron {len(candela_vals)}")
        if len(candela_vals) % num_ang_vert == 0:
            num_ang_horiz = len(candela_vals) // num_ang_vert
        elif len(candela_vals) % num_ang_horiz == 0:
            num_ang_vert = len(candela_vals) // num_ang_horiz
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

uploaded_file = st.file_uploader("🔧 Suba un archivo .IES", type=["ies"])
if uploaded_file is not None:
    try:
        C, theta, flujo_total, nh, nv = leer_ies(uploaded_file.read())
        cu, flujo_util = calcular_cu(C, theta, flujo_total)

        st.success(f"✅ Archivo procesado")
        st.write(f"📏 Ángulos verticales: {nv}")
        st.write(f"🧭 Planos horizontales: {nh}")
        st.write(f"🔸 Flujo útil: {round(flujo_util, 2)} lm")
        st.write(f"🔸 Flujo total: {flujo_total} lm")
        st.write(f"🔹 CU real calculado: {round(cu, 3)}")
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
