"""
RIR-API - Milestone 1: Generación de señales
Validación del barrido senoidal logarítmico (Sine Sweep).

Objetivo:
    Verificar el funcionamiento del generador de sine sweep
    y su filtro inverso mediante representaciones gráficas.

Fundamento:
    El barrido senoidal logarítmico permite excitar un sistema
    acústico recorriendo un intervalo de frecuencias.

    La convolución del barrido con su filtro inverso debe
    producir una señal concentrada alrededor de un impulso.

Referencia:
    Farina, A. (2000). Simultaneous measurement of impulse
    response and distortion with a swept-sine technique.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve

from app.services.sine_sweep import generate_sine_sweep_pair


# ---------------------------------------------------------
# 1. Configuración de los parámetros de generación
# ---------------------------------------------------------

fs = 44100          # Frecuencia de muestreo [Hz]
duracion = 2.0      # Duración del barrido [s]
f1 = 20             # Frecuencia inicial [Hz]
f2 = 20000          # Frecuencia final [Hz]


# ---------------------------------------------------------
# 2. Generación del barrido y su filtro inverso
# ---------------------------------------------------------

sweep, inverso = generate_sine_sweep_pair(
    duration=duracion,
    f1=f1,
    f2=f2,
    fs=fs
)


# ---------------------------------------------------------
# 3. Convolución para validar el filtro inverso
# ---------------------------------------------------------

# La convolución debe concentrar la energía en un pico,
# aproximándose a una respuesta impulsiva.

respuesta = fftconvolve(sweep, inverso, mode="full")


# ---------------------------------------------------------
# 4. Construcción de los ejes temporales
# ---------------------------------------------------------

t = np.arange(len(sweep)) / fs
t_respuesta = np.arange(len(respuesta)) / fs


# ---------------------------------------------------------
# 5. Representación gráfica de los resultados
# ---------------------------------------------------------

fig, axes = plt.subplots(3, 1, figsize=(12, 9))

# Gráfico 1: señal de excitación
axes[0].plot(t, sweep)
axes[0].set_title("Barrido senoidal logarítmico")
axes[0].set_xlabel("Tiempo [s]")
axes[0].set_ylabel("Amplitud")
axes[0].grid(True)

# Gráfico 2: filtro inverso
axes[1].plot(t, inverso)
axes[1].set_title("Filtro inverso del sine sweep")
axes[1].set_xlabel("Tiempo [s]")
axes[1].set_ylabel("Amplitud")
axes[1].grid(True)

# Gráfico 3: resultado de la convolución
axes[2].plot(t_respuesta, respuesta)
axes[2].set_title("Convolución del barrido con el filtro inverso")
axes[2].set_xlabel("Tiempo [s]")
axes[2].set_ylabel("Amplitud")
axes[2].grid(True)

plt.tight_layout()


# ---------------------------------------------------------
# 6. Exportación de las gráficas
# ---------------------------------------------------------

plt.savefig("validacion_sine_sweep.png", dpi=150)

# Mostrar los resultados
plt.show()

