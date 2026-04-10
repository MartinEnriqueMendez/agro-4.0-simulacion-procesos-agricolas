"""
PROYECTO: Agro 4.0 - Simulación de Riego del Limón (Yungas Jujeñas)
MODELO: Simulación de Monte Carlo para optimización hídrica.
DESCRIPCIÓN: Este modelo evalúa el impacto de la Agricultura de Precisión e IA 
             en la reducción del consumo de agua, considerando variables 
             climáticas estocásticas.
AUTOR: Ing. Martín Enrique Méndez
"""

import numpy as np
import matplotlib.pyplot as plt

# Configuración de reproducibilidad para validación de resultados
np.random.seed(42)

# --- PARÁMETROS GENERALES DE LA SIMULACIÓN ---
n_sims   = 10000      # Número de iteraciones de Monte Carlo
n_hect   = 50         # Muestra de hectáreas analizadas
n_days   = 120        # Ciclo temporal (Primavera - Verano)
cons_m   = 500        # Consumo medio base (L/ha·día)
cons_sd  = 50         # Desviación estándar del consumo
mu_p, sd_p = 10, 10   # Lluvia Primavera (Media y Desviación)
mu_v, sd_v = 50, 10   # Lluvia Verano (Media y Desviación)

# --- DEFINICIÓN DE ESCENARIOS AGRO 4.0 ---
# Representan el % de eficiencia adicional aportado por cada tecnología
effs = {
    'Sin tecnología':           0.0,
    'Agricultura de precisión': 0.2, # ~20% ahorro por sensores de humedad
    'Inteligencia artificial':  0.3, # ~30% ahorro por detección de malezas/hongos
    'Ambas tecnologías':        0.4  # ~40% ahorro combinado
}

colores = {
    'Sin tecnología':           'blue',
    'Agricultura de precisión': 'gold',
    'Inteligencia artificial':  'green',
    'Ambas tecnologías':        'purple'
}

def generar_lluvia(mu, sigma, size):
    """Genera una serie temporal de lluvia acumulada usando distribución normal."""
    inc = np.random.normal(mu, sigma, size)
    return np.cumsum(inc)

def simular_escenario(eff_label):
    """
    Simula un escenario específico de consumo hídrico.
    Aplica las eficiencias tecnológicas basadas en condiciones de humedad y riesgo.
    """
    # Generación de variables climáticas
    lp = generar_lluvia(mu_p, sd_p, n_days)
    lv = generar_lluvia(mu_v, sd_v, n_days)
    lluvia = (lp + lv) / 2

    # Consumo teórico y cálculo de exceso (riego necesario)
    c = np.random.normal(cons_m, cons_sd, (n_hect, n_days))
    exceso = np.maximum(c - lluvia, 0)

    # Variables aleatorias de estado (Humedad y Riesgo Fúngico)
    hum  = np.random.rand(n_hect, n_days) 
    risk = np.random.rand(n_hect, n_days) 

    # Aplicación de lógica de ahorro tecnológico
    if eff_label == 'Agricultura de precisión':
        exceso[hum < 0.5] *= (1 - effs[eff_label])
    elif eff_label == 'Inteligencia artificial':
        exceso[risk < 0.5] *= (1 - effs[eff_label])
    elif eff_label == 'Ambas tecnologías':
        exceso[hum < 0.5] *= (1 - effs['Agricultura de precisión'])
        exceso[risk < 0.5] *= (1 - effs['Inteligencia artificial'])

    return exceso.sum() / (n_hect * n_days)

# --- EJECUCIÓN DEL MOTOR DE SIMULACIÓN ---
resultados = {esc: np.zeros(n_sims) for esc in effs}
for i in range(n_sims):
    for esc in effs:
        resultados[esc][i] = simular_escenario(esc)

# --- ANÁLISIS DE MÉTRICAS Y PRECISIÓN ---
cons_esp_base = cons_m - (mu_p + mu_v) / 2
cons_esp = {esc: cons_esp_base * (1 - effs[esc]) for esc in effs}

def calcular_metricas(res, esp):
    """Calcula errores estadísticos y porcentaje de reducción real."""
    mse = np.mean((res - esp)**2)
    mae = np.mean(np.abs(res - esp))
    re  = np.mean(np.abs((res - esp) / esp)) * 100
    red = ((esp - res.mean()) / esp) * 100
    return mse, mae, re, red

# --- GENERACIÓN DE VISUALIZACIONES ---
fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
axes = axes.flatten()
todos = np.hstack(list(resultados.values()))
xmin, xmax = np.percentile(todos, [1, 99])

for ax, esc in zip(axes, resultados):
    data = resultados[esc]
    ax.hist(data, bins=50, color=colores[esc], edgecolor='black', alpha=0.7)
    m = data.mean()
    ax.axvline(m, color='red', linestyle='--', lw=2)
    ax.text(m*1.02, ax.get_ylim()[1]*0.8, f"μ={m:.1f}", color='red')
    ax.set_title(f"Escenario: {esc}")
    ax.set_xlim(xmin, xmax)
    ax.set_xlabel("Consumo Final (L/ha·día)")
    ax.set_ylabel("Frecuencia (Simulaciones)")
    ax.grid(True, linestyle=':', alpha=0.6)

fig.suptitle("Impacto de Tecnologías Agro 4.0 en el Consumo Hídrico (Monte Carlo)", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Guardar visualización para el repositorio
# plt.savefig('visualizations/histograma_riego_limon.png')
plt.show()

# --- REPORTE DE RESULTADOS ---
print(f"{'ESCENARIO':<30} | {'MSE':<8} | {'MAE':<8} | {'RE (%)':<8} | {'REDUCCIÓN':<10}")
print("-" * 75)
for esc in effs:
    mse, mae, re, red = calcular_metricas(resultados[esc], cons_esp[esc])
    print(f"{esc:<30} | {mse:<8.2f} | {mae:<8.2f} | {re:<8.2f} | {red:.2f}%")