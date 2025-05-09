
# Autor: Eder Helio Martínez Trejo
# Proyecto: Calculadora de luminarias basada en la NOM-025-STPS-2008
# Derechos reservados © 2025. Prohibida su reproducción sin autorización del autor.

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Calculadora de Luminarias", layout="centered")

def exportar_pdf(datos):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    textobject = c.beginText(40, 750)
    textobject.setFont("Helvetica", 12)
    textobject.textLine("Resultado del cálculo de luminarias según la NOM-025-STPS-2008")
    textobject.textLine("")
    for clave, valor in datos.items():
        textobject.textLine(f"{clave}: {valor}")
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def estimar_reflectancia(e1, e2):
    if e2 == 0:
        return 0
    return round(e1 / e2, 2)

def leyenda_cu(valor):
    if valor < 0.5:
        return "Deficiente aprovechamiento lumínico. Revisar distribución y acabados."
    elif valor < 0.65:
        return "Aprovechamiento moderado. Puede optimizarse."
    else:
        return "Buen coeficiente de utilización."

def graficar_spacing(longitud, ancho, spacing_x, spacing_y):
    cols = int(longitud // spacing_x)
    rows = int(ancho // spacing_y)
    total = cols * rows
    fig, ax = plt.subplots()
    ax.set_title("Distribución de Luminarias (Spacing Manual)")
    ax.set_xlim(0, longitud)
    ax.set_ylim(0, ancho)
    ax.set_aspect('equal')
    ax.grid(True)
    x_coords = [spacing_x * (i + 0.5) for i in range(cols)] * rows
    y_coords = []
    for j in range(rows):
        y_coords += [spacing_y * (j + 0.5)] * cols
    ax.scatter(x_coords, y_coords, c="orange", s=100)
    st.pyplot(fig)
    return total

st.title("Calculadora de Luminarias - NOM-025-STPS-2008")
st.markdown("Calcula el número de luminarias o los lux proporcionados en un espacio conforme a la norma.")

lux_dict = {
    "Patios, estacionamientos, exteriores generales": 20,
    "Pasillos, almacenes poco usados, minas subterráneas": 50,
    "Circulación interior, salas de descanso, cuartos de calderas": 100,
    "Inspección visual simple, vigilancia, pailería": 200,
    "Ensamble simple, trabajos en banco, oficinas": 300,
    "Captura de datos, laboratorios, dibujo técnico": 500,
    "Talleres de precisión, inspección de piezas pequeñas": 750,
    "Pulido fino, inspección detallada": 1000,
    "Tareas de alta especialización visual": 2000
}

st.header("1. Tipo de tarea visual")
tarea_visual = st.selectbox("Selecciona el tipo de área o tarea:", list(lux_dict.keys()))
lux_nom = lux_dict[tarea_visual]

st.header("2. Dimensiones del área")
longitud = st.number_input("Longitud del área (m)", min_value=1.0, step=0.5)
ancho = st.number_input("Ancho del área (m)", min_value=1.0, step=0.5)
altura_montaje = st.number_input("Altura de montaje (m)", min_value=1.0, step=0.1)
st.image("altura-colgantes-scaled.jpeg", caption="Altura de montaje: lámparas colgantes")
altura_plano_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.5, value=0.75, step=0.05)
st.image("hola.png", caption="Altura del plano de trabajo")
area = longitud * ancho

st.header("3. Parámetros de luminaria")
flujo_luminoso = st.number_input("Flujo luminoso por lámpara (lúmenes)", min_value=100.0, step=50.0)
mf = st.slider("Índice de mantenimiento (MF)", 0.5, 1.0, 0.8, 0.01)
cu = st.slider("Coeficiente de utilización (CU)", 0.3, 0.9, 0.68, 0.01)
st.caption(leyenda_cu(cu))

with st.expander("¿Quieres estimar reflectancia con luxómetro?"):
    e1 = st.number_input("Lectura pegado a la superficie (lux)", min_value=0.0)
    e2 = st.number_input("Lectura a 10 cm (lux)", min_value=0.0)
    if e1 > 0 and e2 > 0:
        refl_estimada = estimar_reflectancia(e1, e2)
        st.success(f"Reflectancia estimada: {refl_estimada}")

use_spacing = st.checkbox("Usar Spacing Manual (Spacing X / Spacing Y)")
if use_spacing:
    spacing_x = st.number_input("Spacing X (m)", min_value=0.1, step=0.1)
    spacing_y = st.number_input("Spacing Y (m)", min_value=0.1, step=0.1)
    st.markdown("*Esto reemplaza el cálculo por lux objetivo. Se calcularán luminarias según distribución física.*")

st.header("4. Cálculo")
resultado = {}

def calcular_numero_luminarias(lux_requerido, area, flujo_luminoso, CU, MF):
    return (lux_requerido * area) / (flujo_luminoso * CU * MF)

def calcular_luxes_totales(n_luminarias, flujo_luminoso, area, CU, MF):
    return (n_luminarias * flujo_luminoso * CU * MF) / area

if use_spacing:
    num_luminarias = graficar_spacing(longitud, ancho, spacing_x, spacing_y)
    lux_total = calcular_luxes_totales(num_luminarias, flujo_luminoso, area, cu, mf)
    st.subheader(f"Luminarias con spacing definido: {num_luminarias}")
    st.subheader(f"Lux proporcionados: {lux_total:.2f}")
    resultado = {"Modo": "Distribución manual", "Luminarias": num_luminarias, "Lux reales": round(lux_total, 2)}
else:
    modo = st.radio("¿Qué deseas calcular?", ["Número de luminarias a partir de lux", "Lux generados por luminarias"])
    if modo == "Número de luminarias a partir de lux":
        lux_objetivo = st.number_input("Lux deseado (lux)", min_value=10, max_value=2000, value=lux_nom, step=10)
        num_luminarias = calcular_numero_luminarias(lux_objetivo, area, flujo_luminoso, cu, mf)
        st.subheader(f"Luminarias necesarias: {num_luminarias:.2f}")
        resultado = {"Lux deseado": lux_objetivo, "Luminarias necesarias": round(num_luminarias, 2)}
    else:
        num_luminarias = st.number_input("Cantidad de luminarias instaladas", min_value=1, step=1)
        lux_total = calcular_luxes_totales(num_luminarias, flujo_luminoso, area, cu, mf)
        st.subheader(f"Lux proporcionados: {lux_total:.2f}")
        resultado = {"Cantidad de luminarias": num_luminarias, "Lux generados": round(lux_total, 2)}

st.header("5. Exportar resultados")
datos_export = {
    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "Área (m²)": round(area, 2),
    "Flujo luminoso por lámpara (lm)": flujo_luminoso,
    "CU": cu,
    "MF": mf,
    "Altura montaje": altura_montaje,
    "Altura plano trabajo": altura_plano_trabajo,
    **resultado
}
df = pd.DataFrame(list(datos_export.items()), columns=["Parámetro", "Valor"])
excel_buffer = io.BytesIO()
df.to_excel(excel_buffer, index=False, engine="openpyxl")
excel_buffer.seek(0)
st.download_button("📥 Descargar como Excel", data=excel_buffer, file_name="resultado_luminarias.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
pdf_buffer = exportar_pdf(datos_export)
st.download_button("📥 Descargar como PDF", data=pdf_buffer, file_name="resultado_luminarias.pdf", mime="application/pdf")
