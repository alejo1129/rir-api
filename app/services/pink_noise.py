import numpy as np


def generate_pink_noise(duration: float, fs: int) -> np.ndarray:
    """Genera una señal de ruido rosa de la duración especificada.

    Parameters
    ----------
    duration : float
        Duración de la señal en segundos.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Ruido rosa normalizado entre -1 y 1, de largo int(duration * fs).
    """

    n = int(duration * fs)

    # Generamos ruido blanco
    rng = np.random.default_rng()
    white = rng.standard_normal(n)

    # Pasamos la señal al dominio de la frecuencia
    spectrum = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, d=1 / fs)

    # Aplicamos la caída característica del ruido rosa
    scale = np.zeros_like(freqs)
    scale[1:] = 1 / np.sqrt(freqs[1:])
    spectrum = spectrum * scale

    # Volvemos al dominio del tiempo
    pink = np.fft.irfft(spectrum, n=n)

    # Normalizamos entre -1 y 1
    max_value = np.max(np.abs(pink))
    if max_value > 0:
        pink = pink / max_value

    return pink
