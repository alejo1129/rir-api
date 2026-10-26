"""Servicio de filtrado por bandas de octava.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

import numpy as np
from scipy import signal as sps


def filter_single_band(
    signal: np.ndarray, fs: int, center_freq: float, order: int = 4
) -> np.ndarray:
    """Aplica un filtro pasabanda de una octava centrado en `center_freq` (IEC 61260)."""
    signal_arr = np.asarray(signal, dtype=np.float64)

    # 1. Calculamos las frecuencias de corte inferior y superior de la octava
    f_low = center_freq / np.sqrt(2.0)
    f_high = center_freq * np.sqrt(2.0)

    # 2. Nos aseguramos de no pasarnos de la frecuencia de Nyquist (fs / 2)
    nyquist = fs / 2.0
    if f_high >= nyquist:
        f_high = nyquist * 0.999

    # 3. Disenamos el filtro Butterworth pasabanda en formato SOS
    sos = sps.butter(
        N=order,
        Wn=[f_low, f_high],
        btype="bandpass",
        fs=fs,
        output="sos",
    )

    # 4. Aplicamos el filtro con fase cero (ida y vuelta)
    filtered = sps.sosfiltfilt(sos, signal_arr)

    return filtered.astype(np.float64)
