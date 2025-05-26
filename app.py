import numpy as np
import matplotlib.pyplot as plt

print("🔧 Suba el archivo .IES para calcular el CU")

# === Leer archivo .IES ===
def leer_ies(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='latin1') as f:
        lines = f.readlines()

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
        print(f"⚠️ Aviso: se esperaban {expected_vals} candelas, pero se encontraron {len(candela_vals)}")
        if len(candela_vals) % num_ang_vert == 0:
            num_ang_horiz = len(candela_vals) // num_ang_vert
            print(f"🔁 Ajustando número de planos horizontales a {num_ang_horiz}")
        else:
            raise ValueError("La cantidad de candelas no coincide con los ángulos especificados.")

    C = np.array(candela_vals).reshape((num_ang_horiz, num_ang_vert))
    theta_vals = np.array(angulo_vert[:num_ang_vert])
    return C, theta_vals, flujo_total, num_ang_horiz, num_ang_vert


# === Calcular CU ===
def calcular_cu(C, theta_vals, flujo_total):
    mask = theta_vals <= 90
    theta_rad = np.radians(theta_vals[mask])
    I_avg = np.mean(C, axis=0)[mask]

    from numpy import trapezoid
    flujo_util = trapezoid(I_avg * np.sin(theta_rad) * 2 * np.pi * np.cos(theta_rad), theta_rad)
    CU = flujo_util / flujo_total
    return CU, flujo_util


# === Ejecución ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("❗ Error: Proporcione el nombre del archivo .IES como argumento.")
    else:
        archivo = sys.argv[1]
        try:
            C, theta, flujo_total, nh, nv = leer_ies(archivo)
            cu, flujo_util = calcular_cu(C, theta, flujo_total)

            print(f"\n✅ Archivo: {archivo}")
            print(f"📏 Ángulos verticales: {nv}")
            print(f"🧭 Planos horizontales: {nh}")
            print(f"🔸 Flujo útil: {round(flujo_util, 2)} lm")
            print(f"🔸 Flujo total: {flujo_total} lm")
            print(f"🔹 CU real calculado: {round(cu, 3)}")

        except Exception as e:
            print(f"❌ Error al procesar el archivo .IES: {e}")
