"""Servicio de generacion de sine sweep logaritmico.

Milestone 1: Generacion de senales.
"""

import numpy as np


def generate_sine_sweep_pair(
    duration: float, f1: float, f2: float, fs: int
) -> tuple[np.ndarray, np.ndarray]:
    """Genera un barrido senoidal logaritmico y su filtro inverso.

    Parameters
    ----------
    duration : float
        Duracion del barrido en segundos.
    f1 : float
        Frecuencia inicial del barrido en Hz.
    f2 : float
        Frecuencia final del barrido en Hz.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        Tupla con el sine sweep y su filtro inverso, ambos normalizados
        entre -1 y 1.
    """
    n_samples = int(duration * fs)
    t = np.arange(n_samples, dtype=np.float64) / fs

    # Razon logaritmica entre la frecuencia final e inicial: ln(f2 / f1)
    r = np.log(f2 / f1)

    # 1. Generamos el barrido senoidal (formula de Farina)
    phase = (2.0 * np.pi * f1 * duration / r) * (np.exp(t * r / duration) - 1.0)
    sweep = np.sin(phase)

    # Normalizamos el sweep entre -1 y 1
    max_sweep = np.max(np.abs(sweep))
    if max_sweep > 0:
        sweep = sweep / max_sweep

    # 2. Generamos el filtro inverso:
    # Damos vuelta el sweep en el tiempo (sweep[::-1]) y lo multiplicamos
    # por una envolvente exponencial que compensa la energia de los graves
    envelope = np.exp(-t * r / duration)
    inverse_filter = sweep[::-1] * envelope

    # Normalizamos el filtro inverso entre -1 y 1
    max_inv = np.max(np.abs(inverse_filter))
    if max_inv > 0:
        inverse_filter = inverse_filter / max_inv

    return sweep.astype(np.float64), inverse_filter.astype(np.float64)
