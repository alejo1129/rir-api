"""Servicio de reproduccion y grabacion simultanea.

Milestone 1: Generacion de senales.

``sounddevice`` se importa **dentro** de la funcion (import perezoso): asi el
resto de la API, los tests y el CI funcionan en maquinas sin placa de audio.
"""

import numpy as np


def play_and_record(signal: np.ndarray, fs: int, record_duration: float) -> np.ndarray:
    """Reproduce una senal y graba simultaneamente (``sounddevice.playrec``)."""
    try:
        import sounddevice as sd
    except Exception as err:
        raise RuntimeError(
            "No se pudo inicializar el dispositivo de audio. Verifique que sounddevice "
            "y los drivers PortAudio esten correctamente instalados."
        ) from err

    # Calcular el numero total de muestras a grabar
    num_samples = int(record_duration * fs)

    try:
        # playrec reproduce la senal y graba simultaneamente durante num_samples
        recorded = sd.playrec(
            signal,
            samplerate=fs,
            channels=1,
            frames=num_samples,
            dtype="float32",
        )
        sd.wait()  # Espera a que termine la reproduccion/grabacion

        # Asegurar que el array retornado respete exactamente la duracion pedida (num_samples)
        if recorded is not None and len(recorded) != num_samples:
            pad_len = num_samples - len(recorded)
            if pad_len > 0:
                pad_width = (0, pad_len) if recorded.ndim == 1 else ((0, pad_len), (0, 0))
                recorded = np.pad(recorded, pad_width)
            else:
                recorded = recorded[:num_samples]

        return recorded
    except Exception as err:
        raise RuntimeError(
            f"Error durante la reproduccion/grabacion de audio: {err}"
        ) from err
