# Autor: Eder Helio Martinez Trejo
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json

st.set_page_config(page_title="Calculadora de Luminarias NOM-025 + Conelec")

with open("luminarias_conelec_15_COMPLETAS.json", "r", encoding="utf-8") as f:
    luminarias = json.load(f)
with open("areas_nom_025.json", "r", encoding="utf-8") as f:
    areas = json.load(f)

def calcular_rcr(largo_cm, ancho_cm, hfc_cm):
    largo = largo_cm / 100
    ancho = ancho_cm / 100
    hfc = hfc_cm / 100
    return (5 * hfc * (largo + ancho)) / (largo * ancho)

st.header("1️⃣ Dimensiones del Área (en cm)")
largo_cm = st.number_input("Largo del área (cm)", min_value=100, step=10)
ancho_cm = st.number_input("Ancho del área (cm)", min_value=100, step=10)

st.header("2️⃣ Alturas (en cm)")
hcc = st.number_input("Altura de montaje de la luminaria (hcc)", help="Del piso al centro de la luminaria")
hrc = st.number_input("Altura del plano de trabajo (hrc)", help="Altura de la mesa o zona de trabajo (~75 cm)")
hfc = hcc - hrc
st.markdown(f"**Altura entre luminaria y plano de trabajo (hfc):** `{hfc:.2f} cm`")

st.header("3️⃣ Reflectancias del recinto")

st.markdown("""
### 📊 Tabla orientativa de reflectancias

| Elemento  | Tipo de superficie               | Reflectancia típica (ρ) |
|-----------|----------------------------------|--------------------------|
| Techo     | Pintura blanca, yeso             | 0.7 - 0.9                |
| Paredes   | Pintura clara, superficies lisas | 0.5 - 0.7                |
| Piso      | Madera, loseta, concreto pulido  | 0.2 - 0.4                |

- Si usas valores altos (ej. 0.8), estás simulando un recinto muy reflectante.  
- Si los valores son bajos (ej. 0.3), simulas un recinto oscuro, lo cual puede bajar el CU.  
- **Consejo:** Usa valores representativos del acabado real del lugar.
""")

pcc = st.slider("Reflectancia del techo (ρcc)", 0.1, 0.9, 0.7, step=0.05)
ppp = st.slider("Reflectancia de paredes (ρpp)", 0.1, 0.9, 0.5, step=0.05)
pcf = st.slider("Reflectancia del piso (ρcf)", 0.1, 0.5, 0.2, step=0.05)

st.header("4️⃣ Tipo de Área según la NOM-025")
tipo_area = st.selectbox("Selecciona el tipo de área:", [a["area"] for a in areas])
lux_requerido = next(a["lux_recomendado"] for a in areas if a["area"] == tipo_area)
st.markdown(f"**Nivel mínimo recomendado:** `{lux_requerido} lux`")

st.header("5️⃣ Luminaria Conelec")
nombres_luminarias = [l["nombre"] for l in luminarias]
luminaria_sel = st.selectbox("Selecciona una luminaria:", nombres_luminarias)
l = next(l for l in luminarias if l["nombre"] == luminaria_sel)
flujo_lum = l["flujoLuminoso"]

cu = None
mf = None

st.header("6️⃣ Cálculo del CU con RCR")
if largo_cm > 0 and ancho_cm > 0 and hfc > 0:
    rcr = calcular_rcr(largo_cm, ancho_cm, hfc)
    rcr_redondeado = int(round(rcr))
    st.markdown(f"**RCR calculado:** `{rcr:.2f}` → **Usado:** `{rcr_redondeado}`")

    if l["tipo"] == "Campana":
        cu = 0.68 if rcr_redondeado <= 2 else 0.6
    elif l["tipo"] == "Reflector":
        cu = 0.64 if rcr_redondeado <= 2 else 0.58
    else:
        cu = 0.6 if rcr_redondeado <= 2 else 0.5

    mf = 0.8
    st.markdown(f"**CU automático:** `{cu}`")
    st.markdown(f"**MF estimado:** `{mf}`")

st.header("7️⃣ ¿Qué deseas calcular?")
modo = st.radio("Selecciona una opción:", ["Número de luminarias", "Nivel de luxes alcanzado"])
area_m2 = (largo_cm / 100) * (ancho_cm / 100)

if flujo_lum > 0 and cu and mf and area_m2 > 0:
    if modo == "Número de luminarias":
        N = (lux_requerido * area_m2) / (flujo_lum * cu * mf)
        N = int(np.ceil(N))
        E = (N * flujo_lum * cu * mf) / area_m2
        st.success(f"🔢 Luminarias requeridas: {N}")
        st.info(f"💡 Lux generados con {N} luminaria(s): {E:.2f} lux")
    else:
        N = st.number_input("Número de luminarias instaladas", min_value=1, step=1)
        E = (N * flujo_lum * cu * mf) / area_m2
        N_req = int(np.ceil((lux_requerido * area_m2) / (flujo_lum * cu * mf)))
        st.success(f"💡 Nivel de iluminancia estimado: {E:.2f} lux")
        st.info(f"🔢 Luminarias necesarias para cumplir la NOM: {N_req}")

st.header("8️⃣ Distribución estimada de luminarias")
def generar_distribucion(largo_cm, ancho_cm, num_luminarias):
    largo = largo_cm / 100
    ancho = ancho_cm / 100
    filas = int(np.ceil(np.sqrt(num_luminarias * (ancho / largo))))
    columnas = int(np.ceil(num_luminarias / filas))
    x_spacing = largo / (columnas + 1)
    y_spacing = ancho / (filas + 1)
    x_coords = [x_spacing * (i + 1) * 100 for i in range(columnas)] * filas
    y_coords = []
    for j in range(filas):
        y_coords += [y_spacing * (j + 1) * 100] * columnas
    fig, ax = plt.subplots()
    ax.scatter(x_coords[:num_luminarias], y_coords[:num_luminarias], c='orange', s=150, edgecolors='black')
    ax.set_xlim(0, largo_cm)
    ax.set_ylim(0, ancho_cm)
    ax.set_title("Distribución estimada de luminarias (cm)")
    ax.set_xlabel("Largo (cm)")
    ax.set_ylabel("Ancho (cm)")
    ax.grid(True)
    ax.set_aspect("equal")
    return fig

if largo_cm > 0 and ancho_cm > 0 and 'N' in locals() and N > 0:
    st.pyplot(generar_distribucion(largo_cm, ancho_cm, int(N)))
