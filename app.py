import streamlit as st
import re
import math
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Calculadora de Iluminación - NOM-025 + IES", layout="centered")
st.title("🔆 Calculadora de Iluminación con archivo .IES")

st.markdown("""
### 🧭 Introducción
Esta herramienta permite calcular el número de luminarias necesarias para cumplir con los requerimientos de iluminancia establecidos en la **NOM-025-STPS-2008**, utilizando el método de la cavidad zonal.

### 🎯 Objetivo
- Calcular luminarias a partir de archivos `.IES` reales.
- Estimar automáticamente el área, RCR, CU y FM.
- Aplicar los niveles de iluminación requeridos según el tipo de actividad.
- Visualizar la distribución estimada de luminarias.
- Explicar conceptos clave como reflectancias, alturas y mantenimiento.

### 🎨 ¿Qué son las reflectancias?
Las reflectancias indican qué tanta luz reflejan las superficies del recinto:
- **Techo (ρcc)**: usualmente blanco o claro. Afecta la luz indirecta descendente.
- **Paredes (ρpp)**: paredes claras reflejan más luz útil.
- **Piso (ρcf)**: los pisos oscuros absorben más luz, pero también existen pisos claros como mármol o cerámica brillante que pueden reflejar bien la luz.

Usar valores correctos mejora la precisión del cálculo del **CU (Coeficiente de Utilización)**.

### 🧼 ¿Qué es el Factor de Mantenimiento (FM)?
El **FM** representa la reducción esperada del flujo luminoso con el paso del tiempo, debido a:
- Acumulación de polvo o suciedad en las luminarias y superficies.
- Degradación del rendimiento de las lámparas.
- Condiciones ambientales y frecuencia de limpieza.

Valores típicos del FM van de **0.5** a **0.8**, siendo:
- **0.8** para ambientes limpios con buen mantenimiento.
- **0.7** para áreas con polvo moderado o limpieza ocasional.
- **0.6 o menos** para zonas industriales o sin mantenimiento.

Este factor se aplica para garantizar que la iluminación calculada siga cumpliendo con la norma incluso tras un periodo prolongado de uso.

### 🎨 Tabla de FM por tipo de ambiente

| Tipo de ambiente                                | FM sugerido |
|--------------------------------------------------|-------------|
| 🟢 Ambiente limpio (oficinas, laboratorios)       | 0.8         |
| 🟡 Moderadamente sucio (uso general, almacenes)   | 0.7         |
| 🟠 Industrial ligero/agresivo                     | 0.6         |
| 🔴 Ambiente severo / mantenimiento deficiente     | 0.5         |
""")

uploaded_file = st.file_uploader("📥 Sube tu archivo .IES para extraer el flujo luminoso", type=["ies"])

def extraer_flujo_luminoso(archivo):
    contenido = archivo.read().decode("latin1").splitlines()
    for linea in contenido:
        if "LUMEN" in linea.upper() or "_TOTALLUMINAIRELUMENS" in linea.upper():
            valores = re.findall(r'\d+\.?\d*', linea)
            if valores:
                return float(valores[0])
    texto_completo = " ".join(contenido)
    numeros = re.findall(r'\d+\.?\d*', texto_completo)
    numeros = list(map(float, numeros))
    try:
        return numeros[8]
    except:
        return None

flujo = extraer_flujo_luminoso(uploaded_file) if uploaded_file else None
if flujo:
    st.success(f"✅ Flujo luminoso extraído: {flujo} lm")
else:
    flujo = st.number_input("Flujo luminoso (lm)", min_value=0.0)

st.subheader("📐 Parámetros del recinto")
largo = st.number_input("Largo del recinto (m)", min_value=0.0)
ancho = st.number_input("Ancho del recinto (m)", min_value=0.0)
area = largo * ancho
st.markdown(f"**Área calculada automáticamente:** `{area:.2f} m²`")

col1, col2 = st.columns(2)
with col1:
    h_montaje = st.number_input("Altura de montaje de la luminaria (m)", min_value=0.0, help="Distancia desde el piso hasta el centro de la luminaria.")
with col2:
    h_trabajo = st.number_input("Altura del plano de trabajo (m)", min_value=0.0, value=0.8, help="Altura donde se realiza la tarea, como escritorios o mesas.")

h_efectiva = h_montaje - h_trabajo
rcr = 0
if h_efectiva > 0 and largo > 0 and ancho > 0:
    rcr = round(5 * (largo + ancho) / (largo * ancho) * h_efectiva, 2)
st.markdown(f"**Índice de Cavidad del Recinto (RCR):** `{rcr}`")
