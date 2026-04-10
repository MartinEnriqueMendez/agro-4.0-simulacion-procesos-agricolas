"""
PROYECTO: Agro 4.0 - Dinámica de Suelo y Crecimiento de Maíz (Yungas)
MODELO: Sistema de Ecuaciones Diferenciales Ordinarias (EDO).
DESCRIPCIÓN: Modelado multivariable que integra Temperatura, Aireación, Nutrientes, 
             Humedad y pH para predecir el crecimiento del Maíz Pisingallo.
AUTOR: Ing. Martín Enrique Méndez
"""

import numpy as np 
from scipy.integrate import odeint 
import matplotlib.pyplot as plt
import seaborn as sns

# --- PARÁMETROS DE DINÁMICA TÉRMICA Y HÍDRICA ---
A = 5     # Constante de transferencia de calor 
B = 1     # Constante de evaporación 
Ta = 29.5 # Temperatura ambiente 
Ho = 0.6  # Humedad óptima (60%) 
varest = 14 # Variación estacional (%)

# Eventos de lluvia intensos y su "intensidad" relativa (0–1)
lluvias = {10: 0.5, 30: 0.8, 50: 0.6}

# --- PARÁMETROS BIOLÓGICOS (MAÍZ) ---
crecmax = 3             # Crecimiento máximo (m)
kcrecimiento = 0.005    # Constante de crecimiento
ktempoptima = 0.003     # Constante de temperatura óptima
kairoptima = 0.004      # Constante de aireación óptima

# --- PARÁMETROS DE SUELO Y NUTRIENTES ---
absorcionagua = 0.25    # Absorción del suelo (cm/h)
Po = 0.018              # Precipitación óptima
evaporacion = 0.003     # Evaporación (mm/día)
To = 15                 # Temperatura óptima
difusionoxigeno = 0.0002# Difusión de O2
consumooxigeno = 0.0001 # Consumo de O2
E = 0.04                # Absorción de nutrientes planta
Co = 1                  # Conc. óptima nutrientes
F = 0.5                 # Disponibilidad nutrientes
C = 0.0001              # Absorción suelo
No = 1                  # Conc. óptima
D = 0.0003              # Intercambio aireación
Ao = 1                  # Aireación óptima
k_hum = 0.05            # Relación humedad–pH

# --- DEFINICIÓN DE FUNCIONES DEL SISTEMA (EDOs) ---

def Temperatura(T, H, t):
    fase = 30 
    diT_t = A * (Ta - T) + B * (H - Ho) + varest * np.sin(2 * np.pi * (t - fase) / 120.0)
    return diT_t

def CrecimientoMaiz(N, T, A):
    crecimiento = (kcrecimiento * (N - No) + ktempoptima * (T - To) + kairoptima * (A - Ao)) / crecmax
    return min(crecimiento, crecmax)

def Humedad(P, T, Hu, t):
    base = 38.0
    P_t = sum(int(abs(t - d) < 0.5) * amp * Po for d, amp in lluvias.items())
    diHu_t = absorcionagua * P_t + 0.1 * (base - Hu) - evaporacion * (T - To)
    return max(diHu_t, 0)

def Aireacion(H, T, t):
    diAi_t = difusionoxigeno * (H - Ho) + consumooxigeno * (T - To)
    diAi_t += 0.2 * np.sin(2 * np.pi * t / 30)
    return diAi_t

def Nutrientes(N, T, t):
    diN_t = F * (T - To) * 0.5
    for d, amp in lluvias.items():
        if t >= d: diN_t += amp * 20 * np.exp(-(t - d) / 3)
    return diN_t

def Alcalinidad(diN_t, Ai, diHu_t, t):
    dipH_t = C * (diN_t - No) + D * (Ai - Ao) + k_hum * (diHu_t - Po)
    dipH_t += 0.05 * np.sin(2 * np.pi * t / 40)
    return dipH_t

def sistema(variables, t):
    T, Ai, N, Hu, Al, Cre = variables
    d_T = Temperatura(T, Hu, t)
    d_Ai = Aireacion(Hu, T, t)
    d_N = Nutrientes(N, T, t)
    d_Hu = Humedad(Po, T, Hu, t)
    d_pH = Alcalinidad(d_N, Ai, d_Hu, t)
    d_C = CrecimientoMaiz(N, T, Ai)
    return [d_T, d_Ai, d_N, d_Hu, d_pH, d_C]

# --- EJECUCIÓN DE LA SIMULACIÓN ---

condiciones_iniciales = [27.5, 22.0, 50.0, 35.0, 6.0, 0.0]
tiempototal = np.linspace(0, 130, 1000)
tiemposuelo = np.linspace(0, 60, 600)

soluciontotal = odeint(sistema, condiciones_iniciales, tiempototal)
solucionparcial = odeint(sistema, condiciones_iniciales, tiemposuelo)

# Gráfica de 4 variables de suelo
plt.figure(figsize=(12, 8))
variables_suelo = [
    (solucionparcial[:, 1], "Aireación", "Poros ocupados (%)", 1),
    (solucionparcial[:, 2], "Nutrición", "Nutrientes (ppm)", 2),
    (solucionparcial[:, 3], "Humedad", "Humedad relativa (%)", 3),
    (solucionparcial[:, 4], "Alcalinidad", "Alcalinidad (pH)", 4)
]

for data, title, ylabel, pos in variables_suelo:
    plt.subplot(2, 2, pos)
    plt.plot(tiemposuelo, data, label=title)
    plt.xticks(range(0, 71, 10))
    plt.xlabel("Tiempo (días)"); plt.ylabel(ylabel); plt.title(title)
    plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()

# Gráfica Temperatura y Crecimiento
plt.figure(figsize=(12, 8))
plt.subplot(2, 1, 1)
plt.plot(tiempototal, soluciontotal[:, 0], label="Temperatura", color='orange')
plt.title("Simulación de Temperatura máxima"); plt.grid(True); plt.legend()

plt.subplot(2, 1, 2)
plt.plot(tiempototal, soluciontotal[:, 5], label="Crecimiento Maíz", color='green')
plt.title("Crecimiento del maíz (cm)"); plt.grid(True); plt.legend()
plt.tight_layout(); plt.show()


# --- COMPARATIVA: CON SENSORES VS SIN SENSORES ---

def generar_datos(t, con_sensores=True):
    noise = 0.1 if con_sensores else 0.1
    return (np.sin(2*np.pi*t/60) if con_sensores else np.cos(2*np.pi*t/60)) + np.random.normal(0, noise, t.shape)

tiempo = np.linspace(0, 70, 100)
vars_label = ["Humedad", "Temperatura", "Nutrición"]
unidades = ["%", "°C", "mg/L"]

for i in range(3):
    d_con = generar_datos(tiempo, True)
    d_sin = generar_datos(tiempo, False)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    vmin, vmax = min(d_con.min(), d_sin.min()), max(d_con.max(), d_sin.max())
    
    sns.heatmap(d_con.reshape(1, -1), ax=axes[0], cmap='bwr', vmin=vmin, vmax=vmax, cbar_kws={'label': unidades[i]})
    axes[0].set_title(f'{vars_label[i]} CON sensores')
    
    sns.heatmap(d_sin.reshape(1, -1), ax=axes[1], cmap='bwr', vmin=vmin, vmax=vmax, cbar_kws={'label': unidades[i]})
    axes[1].set_title(f'{vars_label[i]} SIN sensores')
    plt.tight_layout(); plt.show()

# --- IMPACTO EN RENDIMIENTO FINAL ---
dias = np.linspace(0, 130, 1000)
plt.figure(figsize=(10, 5))
plt.plot(dias, 0.05 * dias, label="Sin Sensores")
plt.plot(dias, 0.06 * dias, label="Con Sensores", linewidth='2.5', color='green')
plt.title("Ventaja relativa en crecimiento (cm)"); plt.legend(); plt.grid(True); plt.show()

plt.figure(figsize=(6, 5))
plt.bar(["Sin Sensores", "Con Sensores"], [4000, 4000*1.15], color=["red", "green"])
plt.title("Impacto en Rendimiento Estimado (kg/ha)"); plt.show()
