# **Agro 4.0: Modelado y Simulación de procesos agrícolas respecto a cultivos regionales 🚀🌱**  <br>

El siguiente repositorio contiene los modelos numéricos, simulaciones, gráficos y resultados desarrollados bajo el proyecto de ingenieria que validó mi tesis de grado en Ingeniería en Informática. <br>
El proyecto aplica técnicas de Inteligencia Artificial, Análisis de Eficiencia (DEA) y Sistemas de Ecuaciones Diferenciales para optimizar la producción de Limón, Poroto y Maíz en la región de las Yungas de la provincia de Jujuy.

**📂 Estructura del Proyecto**  

- /models: Scripts de Python con la lógica de simulación y cálculo.

- /data: Conjuntos de datos históricos y parámetros de entrada.

- /visualizations: Resultados gráficos de las simulaciones y comparativas de rendimiento.

**📈 Resumen de los Modelos**  


1. Simulación de Riesgo Hídrico (Limón) - modelolimon-montecarlo.py <br>
Análisis de incertidumbre mediante el método de Monte Carlo para evaluar el impacto de tecnologías 4.0 en el consumo de agua.

Resultado clave: La implementación conjunta de sensores e IA redujo el error cuadrático medio (MSE) de 190,857 a 65,873, logrando una precisión superior al 91% en la gestión de recursos.

2. Eficiencia Productiva (Poroto) - modeloporoto_dea.py <br>
Uso de Data Envelopment Analysis (DEA) y regresiones polinomiales para identificar la frontera de eficiencia en 87 unidades de toma de decisión (DMUs) correspondientes a datos históricos de producciones de poroto.

Resultado clave: Identificación de 54 DMUs eficientes. El modelo detectó una brecha productiva del 38% susceptible de mejora mediante tecnificación.

3. Dinámica de Suelo (Maíz Pisingallo) - modelomaiz_edo.py <br>
Sistema de 6 Ecuaciones Diferenciales Ordinarias (EDO) acopladas que simulan la interacción entre Nutrición, Temperatura, Humedad, Aireación, pH y Crecimiento.

Resultado clave: La simulación demostró un incremento estimado del 15% en el rendimiento (kg/ha) mediante el uso de sensores de precisión para el control de variables críticas.

**🛠️ Tecnologías Utilizadas**  

- **Python 3.x**

- **SciPy & NumPy: Resolución de EDOs y optimización lineal.**

- **Scikit-Learn: Regresiones polinomiales y métricas de error.**

- **Matplotlib & Seaborn: Visualización de datos y mapas de calor.**  

**Autor: Ingeniero Martín Enrique Méndez**  

Universidad Católica de Santiago del Estero, Sede San Salvador - *UCSE DASS*