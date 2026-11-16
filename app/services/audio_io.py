"""Servicio de reproduccion y grabacion simultanea.

Milestone 1: Generacion de senales.

``sounddevice`` se importa **dentro** de la funcion (import perezoso): asi el
resto de la API, los tests y el CI funcionan en maquinas sin placa de audio.
"""

import numpy as np


def play_and_record(signal: np.ndarray, fs: int, record_duration: float) -> np.ndarray:
    """Reproduce una senal y graba simultaneamente usando sounddevice.

    Parameters
    ----------
    signal : np.ndarray
        Senal de audio que se va a reproducir.
    fs : int
        Frecuencia de muestreo en Hz.
    record_duration : float
        Duracion total de la grabacion en segundos. La reproduccion incluye
        0.5 s de silencio inicial como pre-roll.

    Returns
    -------
    np.ndarray
        Senal grabada por el dispositivo de entrada.

    Raises
    ------
    RuntimeError
        Si no se puede inicializar el dispositivo de audio o si ocurre
        un error durante la reproduccion o grabacion.
    """
    try:
        import sounddevice as sd
    except Exception as err:
        raise RuntimeError(
            "No se pudo inicializar el dispositivo de audio. Verifique que sounddevice "
            "y los drivers PortAudio esten correctamente instalados."
        ) from err

    # Calcular el numero total de muestras a grabar.
    num_samples = int(record_duration * fs)

    # Agregar 0.5 s de pre-roll para compensar la latencia del sistema de audio.
    pre_roll_samples = int(0.5 * fs)

    if signal.ndim == 1:
        signal_with_preroll = np.pad(signal, (pre_roll_samples, 0))
    else:
        signal_with_preroll = np.pad(signal, ((pre_roll_samples, 0), (0, 0)))

    # Completar con silencio hasta record_duration o recortar si es necesario.
    if len(signal_with_preroll) < num_samples:
        pad_len = num_samples - len(signal_with_preroll)

        if signal_with_preroll.ndim == 1:
            signal_to_play = np.pad(signal_with_preroll, (0, pad_len))
        else:
            signal_to_play = np.pad(signal_with_preroll, ((0, pad_len), (0, 0)))
    else:
        signal_to_play = signal_with_preroll[:num_samples]

    try:
        recorded = sd.playrec(
            signal_to_play,
            samplerate=fs,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        return recorded
    except Exception as err:
        raise RuntimeError(f"Error durante la reproduccion/grabacion de audio: {err}") from err
