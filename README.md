# Sistema de clasificación de calidad de señales PPG mediante ESP32-S3

## 1. Descripción del proyecto

Este proyecto desarrolla un sistema experimental de adquisición y clasificación de señales fotopletismográficas (PPG), utilizando un microcontrolador ESP32-S3, un sensor óptico MAX30102 y técnicas de aprendizaje automático.

El objetivo es identificar condiciones de adquisición estables y perturbadas, clasificando las señales como aptas o no aptas para su procesamiento posterior.

Este desarrollo constituye una primera etapa del proyecto de Instrumentación Electrónica del Grupo 08, orientado al diseño de un sistema PPG multiespectral para la investigación de métodos no invasivos de estimación de hemoglobina.

## 2. Hardware utilizado

- ESP32-S3-N16R8.
- Sensor óptico MAX30102.
- Cables de conexión I²C.
- Protoboard y alimentación compatible.

## 3. Tecnologías utilizadas

- Arduino IDE y lenguaje C++ para adquisición.
- Python para procesamiento de señales.
- NumPy y Pandas para análisis de datos.
- Matplotlib para visualización.
- Scikit-learn para entrenamiento y evaluación del clasificador.

## 4. Estructura del repositorio

- `firmware/`: programas del ESP32-S3.
- `python/`: adquisición, comparación, procesamiento y clasificación.
- `datos/`: organización de los datos experimentales.
- `modelos/`: modelo entrenado, gráficos y métricas.

## 5. Instalación

Se requiere Python 3.10 o superior y Arduino IDE con soporte para ESP32.

Desde la carpeta `python`, crear un entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

En Arduino IDE se debe instalar la biblioteca SparkFun MAX3010x Pulse and Proximity Sensor Library.

## 6. Ejecución

Para registrar nuevas señales:

```bash
python capturar_dataset.py
```

Para comparar una señal estable con una perturbada:

```bash
python comparar_senales.py
```

Para entrenar el clasificador:

```bash
python entrenar_modelo.py
```

Para evaluar una nueva captura:

```bash
python predecir_nueva.py
```

## 7. Procesamiento e inteligencia artificial

Se utiliza clasificación supervisada mediante un árbol de decisión. Las características consideradas inicialmente incluyen nivel DC, amplitud pulsátil AC, desviación estándar y variabilidad de diferencias entre muestras.

La salida distingue entre condiciones experimentales estables y perturbadas.

## 8. Resultados

En la carpeta `modelos/` se encuentran los gráficos de comparación de señales, el árbol de decisión, la matriz de confusión y las métricas de evaluación.

Los resultados corresponden a una prueba experimental preliminar y no representan una validación clínica universal de calidad de señales PPG.

## 9. Proyección del proyecto

Este desarrollo servirá como punto de partida para incorporar posteriormente fotodetección discreta, acondicionamiento analógico, adquisición multiespectral de cuatro longitudes de onda, supervisión de fuerza de contacto y evaluación automática de calidad.
