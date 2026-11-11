"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Producto final.
"""

import numpy as np
from scipy import signal as sps

from app.services.filter import filter_single_band

OCTAVE_BANDS = (125, 250, 500, 1000, 2000, 4000, 8000)


def apply_smoothing(
    signal: np.ndarray, fs: int, method: str = "hilbert", window_ms: float = 10
) -> np.ndarray:
    """Suaviza una senal y devuelve su envolvente en **amplitud**.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (tipicamente una RI filtrada por banda, array 1D).
    fs : int
        Frecuencia de muestreo en Hz (para convertir ``window_ms`` a muestras).
    method : str, optional
        ``'hilbert'`` (por defecto) o ``'moving_average'``.
    window_ms : float, optional
        Largo de la ventana de media movil en milisegundos (por defecto 10 ms).

    Returns
    -------
    np.ndarray
        Envolvente en amplitud (no negativa), de la misma longitud que ``signal``.

    Raises
    ------
    ValueError
        Si ``method`` no es ``'hilbert'`` ni ``'moving_average'``, o si
        ``window_ms`` no es positivo.
    """
    sig = np.asarray(signal, dtype=np.float64)

    if method == "hilbert":
        analytic_signal = sps.hilbert(sig)
        return np.abs(analytic_signal).astype(np.float64)

    if method == "moving_average":
        if window_ms <= 0:
            raise ValueError("window_ms debe ser mayor que cero.")
        win_len = max(1, int(window_ms * fs / 1000.0))
        kernel = np.ones(win_len, dtype=np.float64) / win_len
        # Envolvente RMS mediante la raiz de la media movil de signal**2
        mean_sq = np.convolve(sig**2, kernel, mode="same")
        return np.sqrt(np.maximum(mean_sq, 0.0)).astype(np.float64)

    raise ValueError(f"Metodo no soportado: {method}. Use 'hilbert' o 'moving_average'.")


def apply_schroeder_integral(ir: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve) en dB.

    ``E[n] = sum_{k=n}^{N-1} h[k]**2`` (integracion inversa, por ejemplo con
    ``np.cumsum`` sobre la senal invertida) y ``L[n] = 10*log10(E[n] / E[0])``.

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (o RI filtrada por banda, array 1D).

    Returns
    -------
    np.ndarray
        Curva de decaimiento en dB, normalizada a 0 dB en la primera muestra,
        de la misma longitud que ``ir``.

    References
    ----------
    .. [1] Schroeder, M. R. (1965). "New method of measuring reverberation
       time." JASA 37(3), 409-412.
    """
    ir = np.asarray(ir, dtype=np.float64)

    if ir.ndim != 1 or ir.size == 0:
        raise ValueError("La respuesta al impulso debe ser un array 1D no vacio")

    if not np.all(np.isfinite(ir)):
        raise ValueError("La respuesta al impulso debe contener valores finitos")

    peak = np.max(np.abs(ir))

    if peak == 0:
        raise ValueError("No se puede normalizar una respuesta al impulso nula")

    # Normalizar para evitar desbordamientos al calcular la energia.
    normalized_ir = ir / peak

    # Integracion inversa de la energia.
    energy = normalized_ir**2
    edc = np.cumsum(energy[::-1])[::-1]

    # Normalizar la energia y convertirla a decibeles.
    with np.errstate(divide="ignore"):
        edc_db = 10.0 * np.log10(edc / edc[0])

    return edc_db


def linear_regression(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Calcula la regresion lineal por minimos cuadrados.

    Parameters
    ----------
    x : np.ndarray
        Variable independiente (tipicamente tiempo en segundos).
    y : np.ndarray
        Variable dependiente (tipicamente curva de Schroeder en dB).

    Returns
    -------
    slope : float
        Pendiente de la recta ajustada ``m`` (dB/s en el contexto acustico).
    intercept : float
        Ordenada al origen ``b`` (dB).
    r2 : float
        Coeficiente de determinacion R^2.
    """
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)

    x_mean = float(np.mean(x_arr))
    y_mean = float(np.mean(y_arr))

    dx = x_arr - x_mean
    dy = y_arr - y_mean

    ss_xx = float(np.sum(dx * dx))
    ss_yy = float(np.sum(dy * dy))
    ss_xy = float(np.sum(dx * dy))

    if ss_xx == 0.0:
        raise ValueError("La varianza de x es cero; no se puede ajustar una recta.")

    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean

    if ss_yy == 0.0:
        r2 = 1.0
    else:
        y_pred = slope * x_arr + intercept
        ss_res = float(np.sum((y_arr - y_pred) ** 2))
        r2 = max(0.0, 1.0 - (ss_res / ss_yy))

    return float(slope), float(intercept), float(r2)


def _decay_time(t: np.ndarray, edc_db: np.ndarray, db_start: float, db_end: float) -> float:
    """Estima el tiempo de reverberacion extrapolado a 60 dB en el rango [db_start, db_end]."""
    mask = np.isfinite(edc_db) & (edc_db <= db_start) & (edc_db >= db_end)
    if np.count_nonzero(mask) < 2:
        return 0.0
    slope, _, _ = linear_regression(t[mask], edc_db[mask])
    if slope >= 0:
        return 0.0
    return float(-60.0 / slope)


def calculate_parameters_from_ir(ir: np.ndarray, fs: int) -> dict[str, dict[float, float]]:
    """Calcula los parametros acusticos ISO 3382 por banda de octava.

    Parametros: EDT (0 a -10 dB), T10 (-5 a -15 dB), T20 (-5 a -25 dB),
    T30 (-5 a -35 dB), D50 (%) y C80 (dB).

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    dict[str, dict[float, float]]
        ``{parametro: {frecuencia_central: valor}}``.
    """
    sig = np.asarray(ir, dtype=np.float64)
    t = np.arange(len(sig), dtype=np.float64) / fs

    results: dict[str, dict[float, float]] = {
        "EDT": {},
        "T10": {},
        "T20": {},
        "T30": {},
        "D50": {},
        "C80": {},
    }

    idx_50ms = min(len(sig), int(0.050 * fs))
    idx_80ms = min(len(sig), int(0.080 * fs))

    for fc in OCTAVE_BANDS:
        if fc * np.sqrt(2.0) >= fs / 2.0:
            continue

        band_ir = filter_single_band(sig, fs, float(fc))
        edc = apply_schroeder_integral(band_ir)

        results["EDT"][fc] = _decay_time(t, edc, 0.0, -10.0)
        results["T10"][fc] = _decay_time(t, edc, -5.0, -15.0)
        results["T20"][fc] = _decay_time(t, edc, -5.0, -25.0)
        results["T30"][fc] = _decay_time(t, edc, -5.0, -35.0)

        sq = band_ir**2
        total_energy = float(np.sum(sq))
        if total_energy > 0:
            early_50 = float(np.sum(sq[:idx_50ms]))
            d50 = (early_50 / total_energy) * 100.0

            early_80 = float(np.sum(sq[:idx_80ms]))
            late_80 = max(float(np.sum(sq[idx_80ms:])), 1e-12)
            c80 = 10.0 * np.log10(max(early_80, 1e-12) / late_80)
        else:
            d50 = 0.0
            c80 = 0.0

        results["D50"][fc] = float(d50)
        results["C80"][fc] = float(c80)

    return results


def apply_lundeby(ir: np.ndarray, fs: int) -> tuple[int, float]:
    """Estima el punto de truncamiento de la RI (metodo de Lundeby)."""
    raise NotImplementedError("Implementar en Milestone 3 (opcional)")
