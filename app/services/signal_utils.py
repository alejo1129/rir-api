"""Utilidades de procesamiento de senales.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal as sps

from app.services.filter import filter_single_band


def load_audio(path: str | Path) -> tuple[np.ndarray, int]:
    """Carga un archivo de audio (al menos WAV y FLAC) y retorna senal y fs."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"El archivo de audio no existe: {file_path}")

    try:
        data, fs = sf.read(str(file_path), dtype="float64", always_2d=False)
    except Exception as exc:
        raise ValueError(
            f"No se pudo leer el archivo '{file_path}' como audio valido: {exc}"
        ) from exc

    # Si es estereo o multicanal, promediamos los canales para obtener mono (1D)
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    data = np.asarray(data, dtype=np.float64)

    max_val = np.max(np.abs(data))
    if max_val > 1.0:
        data = data / max_val

    return data, int(fs)


def generate_synthetic_ir(duration: float, t60_values: dict[float, float], fs: int) -> np.ndarray:
    """Sintetiza una respuesta al impulso con valores de T60 conocidos por banda."""
    n_samples = int(duration * fs)
    t = np.arange(n_samples, dtype=np.float64) / fs
    ir = np.zeros(n_samples, dtype=np.float64)

    rng = np.random.default_rng(42)

    for fc_key, t60 in t60_values.items():
        fc = float(fc_key)
        t60_val = float(t60)
        if t60_val <= 0:
            raise ValueError(f"El valor de T60 debe ser positivo (recibido {t60_val} en {fc} Hz).")

        white = rng.standard_normal(n_samples)
        band_noise = filter_single_band(white, fs, fc)
        max_band = np.max(np.abs(band_noise))
        if max_band > 0:
            band_noise = band_noise / max_band

        alpha = (3.0 * np.log(10.0)) / t60_val
        envelope = np.exp(-alpha * t)

        ir += band_noise * envelope

    max_ir = np.max(np.abs(ir))
    if max_ir > 0:
        ir = ir / max_ir

    return ir.astype(np.float64)


def get_impulse_response(recording: np.ndarray, inverse_filter: np.ndarray) -> np.ndarray:
    """Obtiene la respuesta al impulso mediante deconvolucion de un sine sweep."""
    rec = np.asarray(recording, dtype=np.float64)
    inv = np.asarray(inverse_filter, dtype=np.float64)

    if rec.ndim > 1:
        rec = np.mean(rec, axis=1)

    raw_ir = sps.fftconvolve(rec, inv, mode="full")
    peak_idx = int(np.argmax(np.abs(raw_ir)))
    trimmed_ir = raw_ir[peak_idx:]

    max_val = np.max(np.abs(trimmed_ir))
    if max_val > 0:
        trimmed_ir = trimmed_ir / max_val

    return trimmed_ir.astype(np.float64)


def logarithmic_scale_conversion(signal: np.ndarray) -> np.ndarray:
    """Convierte una senal a escala logaritmica (dB) normalizada."""
    sig = np.asarray(signal, dtype=np.float64)
    abs_sig = np.abs(sig)
    max_val = np.max(abs_sig)

    if max_val == 0:
        return np.full_like(abs_sig, -120.0, dtype=np.float64)

    normalized = np.maximum(abs_sig / max_val, 1e-6)
    db = 20.0 * np.log10(normalized)

    return db.astype(np.float64)
