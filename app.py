# CALCULADORA PROFESIONAL DE ILUMINACIÓN - STREAMLIT
# Autor: Eder Helio Martínez Trejo
# Basado en NOM-025-STPS-2008 y archivos .IES
import streamlit as st
import numpy as np
import math
from scipy.interpolate import RegularGridInterpolator

def interpolar_lineal(x, x0, x1, y0, y1):
    if x1 == x0:
        return y0
    return y0 + ((y1 - y0) / (x1 - x0)) * (x - x0)

def buscar_vecinos(x, lista):
    for i in range(len(lista) - 1):
        if lista[i] <= x <= lista[i + 1]:
            return lista[i], lista[i + 1]
    return lista[0], lista[-1]

# Tablas de CU para tipo 15
rcr_vals = [0.60, 0.80, 1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00, 5.00]
ρcc_vals = [0.80, 0.70, 0.50, 0.30]
ρpp_vals = [0.50, 0.30, 0.10, 0.00]
cu_tipo15 = np.array([
    [[0.60,0.59,0.57,0.55],[0.51,0.50,0.48,0.46],[0.50,0.48,0.46,0.44],[0.48,0.46,0.44,0.42]],
    [[0.69,0.67,0.64,0.62],[0.59,0.57,0.55,0.53],[0.54,0.52,0.50,0.48],[0.52,0.50,0.48,0.46]],
    [[0.77,0.75,0.71,0.68],[0.66,0.64,0.61,0.59],[0.62,0.60,0.58,0.56],[0.59,0.57,0.55,0.53]],
    [[0.84,0.81,0.77,0.74],[0.73,0.70,0.67,0.64],[0.68,0.66,0.63,0.61],[0.65,0.63,0.60,0.58]],
    [[0.88,0.84,0.80,0.77],[0.76,0.73,0.69,0.66],[0.71,0.69,0.65,0.63],[0.68,0.65,0.62,0.60]],
    [[0.94,0.89,0.85,0.82],[0.81,0.78,0.74,0.71],[0.75,0.72,0.69,0.66],[0.71,0.69,0.65,0.63]],
    [[0.98,0.93,0.89,0.85],[0.86,0.83,0.79,0.76],[0.80,0.77,0.74,0.71],[0.76,0.74,0.71,0.69]],
    [[1.03,0.97,0.92,0.88],[0.89,0.86,0.82,0.79],[0.83,0.80,0.77,0.74],[0.79,0.77,0.73,0.71]],
    [[1.10,1.04,0.99,0.95],[0.96,0.93,0.89,0.86],[0.90,0.87,0.84,0.81],[0.86,0.84,0.81,0.78]],
    [[1.15,1.08,1.02,0.98],[0.99,0.96,0.92,0.89],[0.93,0.90,0.87,0.84],[0.89,0.86,0.83,0.80]],
])
interpolador_tipo15 = RegularGridInterpolator((rcr_vals, ρcc_vals, ρpp_vals), cu_tipo15)

st.set_page_config(page_title="Calculadora CU NOM-025", layout="wide")
st.title("💡 Calculadora Profesional de CU (Coeficiente de Utilización)")

modo = st.radio("¿Cómo seleccionar la luminaria?", ["Desde catálogo Conelec", "Subir archivo .IES"])

largo = st.number_input("Largo del recinto (m)", 1.0, value=5.0)
ancho = st.number_input("Ancho del recinto (m)", 1.0, value=4.0)
h_montaje = st.number_input("Altura de montaje (m)", 1.0, value=3.0)
h_trabajo = st.number_input("Altura del plano de trabajo (m)", 0.0, value=0.8)

ρcc = st.number_input("Reflectancia del techo (ρcc)", 0.0, 1.0, 0.7)
ρpp = st.number_input("Reflectancia de paredes (ρpp)", 0.0, 1.0, 0.5)
ρcf = st.number_input("Reflectancia del piso (ρcf)", 0.0, 1.0, 0.2)

h_efectiva = h_montaje - h_trabajo
rcr = round(5 * h_efectiva * (largo + ancho) / (largo * ancho), 2)
cu_resultado = None

if modo == "Desde catálogo Conelec":
    cu_resultado = interpolador_tipo15([[rcr, ρcc, ρpp]])[0]

elif modo == "Subir archivo .IES":
    archivo = st.file_uploader("📂 Sube archivo .IES", type=["ies"])
    if archivo:
        lines = archivo.getvalue().decode("latin1").splitlines()
        angulos = []
        candelas = []
        for line in lines:
            valores = line.strip().split()
            try:
                nums = [float(x) for x in valores]
            except:
                continue
            if len(nums) > 10:
                if not angulos:
                    angulos = nums
                elif not candelas:
                    candelas = nums
                if angulos and candelas:
                    break
        if angulos and candelas:
            n = min(len(angulos), len(candelas))
            ang_rad = np.radians(angulos[:n])
            flujo_util = np.trapz(np.array(candelas[:n]) * np.sin(ang_rad) * 2 * np.pi * np.cos(ang_rad), ang_rad)
            flujo_total = 1200
            cu_resultado = flujo_util / flujo_total

# Ajuste por reflectancia del piso
ρcf_vals = [0.10, 0.20, 0.30]
factores_pcf = [0.95, 1.00, 1.04]
x0, x1 = buscar_vecinos(ρcf, ρcf_vals)
i0, i1 = ρcf_vals.index(x0), ρcf_vals.index(x1)
f0, f1 = factores_pcf[i0], factores_pcf[i1]
factor_pcf = interpolar_lineal(ρcf, x0, x1, f0, f1)

if cu_resultado:
    cu_final = round(cu_resultado * factor_pcf, 3)
    st.success(f"🔷 CU ajustado por reflectancia del piso: {cu_final}")

# FM
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

# Resultados finales
if cu_resultado:
    st.header("📊 Resultados Finales")
    lux_req = st.number_input("Lux requeridos", 50, value=300)
    flujo = st.number_input("Flujo luminoso (lm)", value=1200)
    area = largo * ancho
    n_luminarias = math.ceil((area * lux_req) / (flujo * cu_final * FM))
    st.write(f"💡 Luminarias necesarias: **{n_luminarias}**")
    n_disp = st.number_input("Luminarias disponibles", 1, value=n_luminarias)
    lux_resultante = round((n_disp * flujo * cu_final * FM) / area, 2)
    st.write(f"🔦 Lux resultantes: **{lux_resultante} lux**")

  
 
