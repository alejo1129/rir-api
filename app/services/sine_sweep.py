"""Servicio de generacion de sine sweep logaritmico.

Milestone 1: Generacion de senales.
"""

import numpy as np


def generate_sine_sweep_pair(
    duration: float, f1: float, f2: float, fs: int
) -> tuple[np.ndarray, np.ndarray]:
    """Genera un barrido senoidal logaritmico (sine sweep) y su filtro inverso.

    El sweep es ``x(t) = sin[2*pi*f1*T / ln(f2/f1) * (exp(t*ln(f2/f1)/T) - 1)]``
    y el filtro inverso es el sweep invertido en el tiempo con correccion de
    amplitud ``A(t) = exp(-t*ln(f2/f1)/T)`` (tecnica de Farina, 2000). La
    convolucion ``sweep * inverse_filter`` debe aproximar un impulso.

    Parameters
    ----------
    duration : float
        Duracion del barrido en segundos.
    f1 : float
        Frecuencia inicial del barrido en Hz (tipicamente 20 Hz).
    f2 : float
        Frecuencia final del barrido en Hz (tipicamente 20000 Hz).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    sweep : np.ndarray
        Senal del barrido senoidal, normalizada, de longitud ``int(duration * fs)``.
    inverse_filter : np.ndarray
        Filtro inverso correspondiente, normalizado, de la misma longitud.

    References
    ----------
    .. [1] Farina, A. (2000). "Simultaneous measurement of impulse response
       and distortion with a swept-sine technique." 108th AES Convention.
    """
    if duration <= 0 or f1 <= 0 or f2 <= f1 or fs <= 0:
        raise ValueError("Parámetros del sweep inválidos")

    if f2 >= fs / 2:
        raise ValueError("f2 debe ser menor que la frecuencia de Nyquist")

    n = int(duration * fs)
    t = np.arange(n, dtype=np.float64) / fs

    L = duration / np.log(f2 / f1)

    fase = 2 * np.pi * f1 * L * (np.exp(t / L) - 1)
    sweep = np.sin(fase)

    # Filtro inverso según la técnica de Farina
    inverse_filter = sweep[::-1] * np.exp(-t / L)

    # Normalizar el Barrido
    sweep /= np.max(np.abs(sweep))

    # Normalizar el filtro para que la convolucion 
    # Produzca un impulso de amplitud aproximadamente 1
    from scipy.signal import fftconvolve

    respuesta = fftconvolve(sweep, inverse_filter, mode="full")
    pico = np.max(np.abs(respuesta))

    if pico > 0:
        inverse_filter /= pico
    
    return sweep, inverse_filter

