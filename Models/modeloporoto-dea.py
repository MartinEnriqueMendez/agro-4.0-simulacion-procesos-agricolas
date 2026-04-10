# =============================================================================
# MODELO 2: ANÁLISIS DEA Y REGRESIONES POLINOMIALES (Aplicado a producción de Poroto)
# Proyecto: Agro 4.0 - Simulación de rendimiento y productividad
# AUTOR: Ing. Martín Enrique Méndez
# =============================================================================

import pandas as pd
import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# --- CARGA Y LIMPIEZA DE DATOS ---
# Se utiliza el archivo histórico de producción de la región de las Yungas
#datos = pd.read_csv('ModelosNumericos/SimulacionModeloPoroto - Hoja 1.csv')
datos = pd.read_csv('Simulacion-Agro4.0-Yungas/Models/data/SimulacionModeloPoroto - Hoja 1.csv')
datos = datos.dropna(subset=['Sup. Sembrada (Ha)', 'TemperaturaMedia',
                             'Cantidad de producción (Tn)', 'Superficie Cosechada (Ha)', 'DMU'])

# --- 1. CÁLCULO DE EFICIENCIA DEA (CCR Input-Oriented) ---

X = datos[['Sup. Sembrada (Ha)', 'TemperaturaMedia']].values
Y = datos[['Cantidad de producción (Tn)', 'Superficie Cosechada (Ha)']].values

def calcular_eficiencias_dda(X, Y):
    """Función para determinar la eficiencia relativa de las DMUs (Campañas/Deptos)"""
    n, m = X.shape
    p = Y.shape[1]
    eficiencias = np.zeros(n)
    for i in range(n):
        x0 = X[i]
        y0 = Y[i]
        c = np.zeros(n + 1)
        c[-1] = 1.0
        A_ub, b_ub = [], []
        for k in range(m):
            fila = np.zeros(n + 1)
            fila[:n] = X[:, k]
            fila[-1] = -x0[k]
            A_ub.append(fila)
            b_ub.append(0.0)
        for r in range(p):
            fila = np.zeros(n + 1)
            fila[:n] = -Y[:, r]
            fila[-1] = 0.0
            A_ub.append(fila)
            b_ub.append(-y0[r])
        bounds = [(0, None)] * n + [(0, None)]
        res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=bounds, method='highs')
        eficiencias[i] = res.x[-1] if res.success else np.nan
    return eficiencias
    
eficiencias = calcular_eficiencias_dda(X, Y)
datos['Eficiencia_DEA'] = eficiencias
datos['Eficiente'] = np.isclose(eficiencias, 1.0)
datos['Campaña'] = np.arange(1, len(datos) + 1)

# Reporte de resultados en consola
for i, score in enumerate(eficiencias):
    print(f'DMU {i+1}: {score:.4f}')

print (f"Total de DMUs: {len(datos)} | Eficientes: {sum(datos['Eficiente'])}")

# --- 2. MODELADO ESTADÍSTICO POR DEPARTAMENTO ---

X_inputs = datos[['Sup. Sembrada (Ha)', 'TemperaturaMedia']]
y_produccion = datos['Cantidad de producción (Tn)']
y_cosechada = datos['Superficie Cosechada (Ha)']
departamentos_ordenados = ['Ledesma', 'San Pedro', 'Santa Barbara'] 

for depto in departamentos_ordenados:
    datos_depto = datos[datos['DMU'] == depto].copy()
    if len(datos_depto) == 0: continue

    X_depto = datos_depto[['Sup. Sembrada (Ha)']]
    y_prod_depto = datos_depto['Cantidad de producción (Tn)']
    y_cosec_depto = datos_depto['Superficie Cosechada (Ha)']
    
    # Visualización: Regresión Lineal (Producción y Cosecha)
    plt.figure(figsize = (14, 6))
    plt.subplot(1,2,1)
    model_lineal_prod = LinearRegression().fit(X_depto, y_prod_depto)
    plt.scatter(X_depto, y_prod_depto, color='blue', label='Datos reales')
    plt.plot(X_depto, model_lineal_prod.predict(X_depto), color='gold', 
             label=f'R² = {r2_score(y_prod_depto, model_lineal_prod.predict(X_depto)):.2f}')
    plt.title(f'Regresión Lineal - Producción ({depto})')
    plt.legend(); plt.grid(True)

    plt.subplot(1,2,2)
    model_lineal_cosec = LinearRegression().fit(X_depto, y_cosec_depto)
    plt.scatter(X_depto, y_cosec_depto, color='red', label='Datos reales')
    plt.plot(X_depto, model_lineal_cosec.predict(X_depto), color='forestgreen', 
             label=f'R² = {r2_score(y_cosec_depto, model_lineal_cosec.predict(X_depto)):.2f}')
    plt.title(f'Regresión Lineal - Sup. Cosechada ({depto})')
    plt.legend(); plt.grid(True)
    plt.tight_layout(); plt.show()

    # Visualización: Regresión Polinomial (Grado 2)
    poly_inputs = PolynomialFeatures(degree=2)
    X_poly_depto = poly_inputs.fit_transform(datos_depto[['Sup. Sembrada (Ha)', 'TemperaturaMedia']])
    model_p = LinearRegression().fit(X_poly_depto, y_prod_depto)
    
    plt.figure(figsize = (14, 6))
    plt.subplot(1,2,1)
    plt.scatter(datos_depto['Sup. Sembrada (Ha)'], y_prod_depto, color='blue')
    plt.plot(datos_depto['Sup. Sembrada (Ha)'], model_p.predict(X_poly_depto), 'r-x', label='Polinomial')
    plt.title(f'Regresión Polinomial - Producción ({depto})')
    plt.grid(True); plt.show()
    
    # --- 3. PROYECCIONES Y ANÁLISIS DE EFICIENCIA GLOBAL ---

# Gráfico 3D: Interacción Sup. Sembrada, Temperatura y Producción
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X_inputs['Sup. Sembrada (Ha)'], X_inputs['TemperaturaMedia'], y_produccion, color='blue')
ax.set_title('Regresión Polinomial en 3D (Global)')
plt.show()

# Proyección de Tendencia (Próximas 5 campañas)
X_campaña = datos[['Campaña']]
poly_camp = PolynomialFeatures(degree = 2)
model_prod_camp = LinearRegression().fit(poly_camp.fit_transform(X_campaña), y_produccion)
futuras = pd.DataFrame({'Campaña': np.arange(len(datos) + 1, len(datos) + 6)})
pred_prod = np.maximum(0, model_prod_camp.predict(poly_camp.transform(futuras)))

plt.figure(figsize=(10, 5))
plt.plot(datos['Campaña'], y_produccion, 'o-', label = 'Histórica')
plt.plot(futuras['Campaña'], pred_prod, 'x--', label = 'Proyectada')
plt.title('Tendencia y Proyección de Producción (Global)')
plt.legend(); plt.grid(True); plt.show()

# Evolución Histórica de la Eficiencia DEA
plt.figure(figsize=(10, 5))
plt.plot(datos['Campaña'], datos['Eficiencia_DEA'], 'o-', color = 'purple')
plt.title('Evolución de la eficiencia DEA por campaña (Global)')
plt.grid(True); plt.show()