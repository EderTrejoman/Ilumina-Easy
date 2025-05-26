import streamlit as st
import numpy as np
import math

st.set_page_config(page_title="CU desde archivo .IES", layout="wide")
st.title("📂 Cálculo de CU desde archivo .IES")

# === Subir archivo ===
archivo = st.file_uploader("Sube tu archivo .IES", type=["ies"])

cu_resultado = None
flujo_total = None
if archivo:
    lines = archivo.getvalue().decode("latin1").splitlines()
    angulos = []
    candelas = []
    flujo_real_extraido = None
    leyendo_angulos = False
    leyendo_candelas = False

    # Extraer flujo desde línea estructurada tipo IESNA
    for line in lines:
        if flujo_real_extraido is None:
            partes = line.strip().split()
            if len(partes) >= 2:
                try:
                    if float(partes[1]) > 100:
                        flujo_real_extraido = float(partes[1])
                        break
                except:
                    continue

    vertical_angles = []
    horizontal_angles = []
    candela_values = []
    for idx, line in enumerate(lines):
        if "TILT=NONE" in line:
            try:
                info = lines[idx + 1].split()
                num_lamps = int(info[0])
                flujo_total = float(info[1])
                num_vertical = int(info[2])
                num_horizontal = int(info[3])
                vertical_angles = [float(x) for x in lines[idx + 4].split()]
                horizontal_angles = [float(x) for x in lines[idx + 5].split()]
                for i in range(num_horizontal):
                    linea = lines[idx + 6 + i]
                    datos = [float(x) for x in linea.split()]
                    candela_values.append(datos)
                break
            except:
                continue

    if vertical_angles and candela_values:
        angulos = np.array(vertical_angles)
        candelas = np.mean(np.array(candela_values), axis=0)  # Promedio por ángulo
        ang_rad = np.radians(angulos)
        flujo_util = np.trapz(candelas * np.sin(ang_rad) * 2 * np.pi * np.cos(ang_rad), ang_rad)
        if flujo_real_extraido:
            flujo_total = flujo_real_extraido
        cu_resultado = round(flujo_util / flujo_total, 3)

        st.success(f"📊 CU calculado desde .IES: {round(cu_resultado, 3)}")
        st.info(f"📤 Flujo luminoso total declarado: {round(flujo_total)} lm")

# === Alturas y dimensiones del recinto ===
st.header("📏 Dimensiones del recinto")
largo = st.number_input("Largo (m)", 1.0, value=5.0)
ancho = st.number_input("Ancho (m)", 1.0, value=4.0)
h_montaje = st.number_input("Altura de montaje (m)", 1.0, value=3.0)
h_trabajo = st.number_input("Altura del plano de trabajo (m)", 0.0, value=0.8)

# === Factor de mantenimiento ===
st.header("🛠 Factor de Mantenimiento (FM)")
cat_opciones = {
    "I - Sin aberturas": "I",
    "II - 15% luz arriba / rejillas": "II",
    "III - <15% arriba / rejillas o reflectores": "III",
    "IV - Opaca + translúcida con aberturas": "IV",
    "V - Opaca translúcida sin aberturas": "V",
    "VI - Opaca cerrada": "VI"
}
condiciones = ["Muy limpio", "Limpio", "Medio limpio", "Sucio", "Muy sucio"]
categorias = ["I", "II", "III", "IV", "V", "VI"]
tabla_A = [
    [0.038, 0.071, 0.111, 0.162, 0.301],
    [0.033, 0.068, 0.102, 0.147, 0.188],
    [0.079, 0.106, 0.143, 0.184, 0.236],
    [0.070, 0.131, 0.214, 0.314, 0.452],
    [0.078, 0.128, 0.190, 0.249, 0.321],
    [0.076, 0.145, 0.218, 0.284, 0.396]
]
tabla_B = [0.69, 0.62, 0.70, 0.72, 0.83, 0.88]

cat_legible = st.selectbox("Categoría de luminaria", list(cat_opciones.keys()))
cat = cat_opciones[cat_legible]
cond = st.selectbox("Condición del ambiente", condiciones)
tiempo_meses = st.number_input("Tiempo de operación (meses)", min_value=1.0, value=12.0)
t = tiempo_meses / 12
idx_cat = categorias.index(cat)
idx_cond = condiciones.index(cond)
A = tabla_A[idx_cat][idx_cond]
B = tabla_B[idx_cat]
FM = round(math.exp(-A * (t ** B)), 3)
st.success(f"✅ FM: {FM}")

# === Cálculo de número de luminarias ===
st.header("📊 Cálculo final")
if cu_resultado is not None and flujo_total is not None:
    area = largo * ancho
    lux_req = st.number_input("Lux requeridos", 50, value=300)
    n_luminarias = math.ceil((area * lux_req) / (flujo_total * cu_resultado * FM))
    st.write(f"💡 Luminarias necesarias: **{n_luminarias}**")

    n_disp = st.number_input("Luminarias disponibles", 1, value=n_luminarias)
    lux_resultante = round((n_disp * flujo_total * cu_resultado * FM) / area, 2)
    st.write(f"🔦 Lux resultantes: **{lux_resultante} lux**")
