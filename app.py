# CALCULADORA PROFESIONAL DE ILUMINACIÓN EN GOOGLE COLAB
# Autor: Eder Helio Martínez Trejo
# Basado en NOM-025-STPS-2008 y archivos .IES

# BLOQUE 1: Configuración inicial y subida de archivo .IES
from google.colab import files
import numpy as np
import math
import matplotlib.pyplot as plt

print("🔆 Calculadora de Iluminación (CU real vs estimado) - NOM-025 + .IES")

uploaded = files.upload()

for fname in uploaded.keys():
    with open(fname, 'r', encoding='latin1') as f:
        lines = f.readlines()
        print(f"\n📂 Archivo cargado: {fname}\n")
        print("🧾 Primeras 40 líneas del archivo .IES:")
        for i, line in enumerate(lines[:40]):
            print(f"{i+1:02d}: {line.strip()}")

# BLOQUE 2: Extracción de ángulos y candelas + cálculo de CU real
print("\n📐 Extrayendo ángulos y valores de candela...")

angulos = []
candelas = []

for i, line in enumerate(lines):
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
    flujo_total = 1200  # puedes ajustar este valor si el .IES lo declara distinto
    cu_real = round(flujo_util / flujo_total, 3)
    print(f"\n✅ CU calculado desde .IES (real): {cu_real}")
else:
    print("⚠ No se pudo extraer CU real. Revisa que el archivo tenga tabla de ángulos y candelas válidas.")

# BLOQUE 3: Ingreso de datos del recinto y cálculo de CU estimado
print("\n📏 Ingreso de parámetros del recinto")

largo = float(input("Largo del recinto (m): "))
ancho = float(input("Ancho del recinto (m): "))
area = largo * ancho

h_montaje = float(input("Altura de montaje de la luminaria (m): "))
h_trabajo = float(input("Altura del plano de trabajo (m): "))
h_efectiva = h_montaje - h_trabajo

ρcc = float(input("Reflectancia del techo (ρcc, entre 0 y 1): "))
ρpp = float(input("Reflectancia de las paredes (ρpp, entre 0 y 1): "))
ρcf = float(input("Reflectancia del piso (ρcf, entre 0 y 1): "))

rcr = round(5 * h_efectiva * (largo + ancho) / (largo * ancho), 2)
reflectancia_media = (ρcc + ρpp + ρcf) / 3
cu_estimado = round(0.6 * reflectancia_media * (1 / (1 + math.exp(-rcr + 3))), 3)

print(f"\n📐 Área: {area} m²")
print(f"📐 RCR calculado: {rcr}")
print(f"🔧 CU estimado según fórmula: {cu_estimado}")

# BLOQUE 4: Cálculo del número de luminarias necesarias y FM
print("\n💡 Cálculo del número de luminarias necesarias")

print("\n🏢 Selecciona el tipo de área a iluminar (según NOM-025-STPS-2008):")
print("1. Oficina o aula (300 lux)\n2. Pasillo o circulación (100 lux)\n3. Área exterior (20 lux)")

opcion_area = input("Elige una opción (1-3): ")
if opcion_area == '1':
    lux_requerido = 300
elif opcion_area == '2':
    lux_requerido = 100
elif opcion_area == '3':
    lux_requerido = 20
else:
    lux_requerido = float(input("Ingresa manualmente el nivel de iluminancia requerido (lux): "))

print("\n🛠 Cálculo del Factor de Mantenimiento (FM)")
print("Categoría de mantenimiento:\n1. I\n2. II\n3. III\n4. IV\n5. V\n6. VI")
categoria = int(input("Selecciona categoría (1-6): ")) - 1

print("\nCondición del ambiente:\n1. Muy limpio\n2. Limpio\n3. Medio limpio\n4. Sucio\n5. Muy sucio")
condicion = int(input("Selecciona condición (1-5): ")) - 1

t = float(input("\nTiempo de operación (en meses): "))

# Tabla de valores A y B desde la imagen
tabla_B = [0.69, 0.62, 0.70, 0.72, 0.83, 0.88]
tabla_A = [
    [0.038, 0.071, 0.111, 0.162, 0.301],
    [0.033, 0.068, 0.102, 0.147, 0.188],
    [0.079, 0.106, 0.143, 0.184, 0.236],
    [0.070, 0.131, 0.214, 0.314, 0.452],
    [0.078, 0.128, 0.190, 0.249, 0.321],
    [0.076, 0.145, 0.218, 0.284, 0.396]
]

A = tabla_A[categoria][condicion]
B = tabla_B[categoria]
fm = round(math.exp(-A * (t ** B)), 3)
print(f"\n✅ FM calculado: {fm}")

n_estimado = math.ceil((area * lux_requerido) / (flujo_total * cu_estimado * fm))
n_real = math.ceil((area * lux_requerido) / (flujo_total * cu_real * fm))

print(f"\n💡 Luminarias con CU estimado: {n_estimado}")
print(f"💡 Luminarias con CU real (.IES): {n_real}")
print(f"🔻 Diferencia: {n_estimado - n_real} luminarias")

# BLOQUE 5: Modo inverso
print("\n🔁 Modo inverso: ¿Qué nivel de lux se obtiene con cierto número de luminarias?")
n_usuario = int(input("Ingresa el número de luminarias disponibles: "))

lux_estimado_cu_real = round((n_usuario * flujo_total * cu_real * fm) / area, 2)
lux_estimado_cu_estimado = round((n_usuario * flujo_total * cu_estimado * fm) / area, 2)

print(f"\n🔦 Lux obtenido con CU real (.IES): {lux_estimado_cu_real} lux")
print(f"🔦 Lux obtenido con CU estimado: {lux_estimado_cu_estimado} lux")

if lux_estimado_cu_real < lux_requerido:
    print(f"⚠ Advertencia: Con CU real, el nivel de iluminancia está por debajo del requerido ({lux_requerido} lux).")
else:
    print("✅ Con CU real, se cumple el nivel de iluminancia requerido.")

if lux_estimado_cu_estimado < lux_requerido:
    print(f"⚠ Advertencia: Con CU estimado, el nivel de iluminancia está por debajo del requerido ({lux_requerido} lux).")
else:
    print("✅ Con CU estimado, se cumple el nivel de iluminancia requerido.")
