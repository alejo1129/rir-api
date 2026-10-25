"""Servicio de reproduccion y grabacion simultanea.

Milestone 1: Generacion de senales.

``sounddevice`` se importa **dentro** de la funcion (import perezoso): asi el
resto de la API, los tests y el CI funcionan en maquinas sin placa de audio.
"""

import numpy as np


def play_and_record(signal: np.ndarray, fs: int, record_duration: float) -> np.ndarray:
    """Reproduce una senal y graba simultaneamente (``sounddevice.playrec``).

    Consideraciones:

    - ``record_duration`` debe ser mayor o igual a la duracion de la senal
      para capturar la cola de reverberacion del recinto.
    - Aceptar senales mono (array 1D) y estereo (array 2D ``(muestras, canales)``)
      sin asumir la forma.
    - Se recomienda un silencio inicial (pre-roll) de 0.5-1 s para compensar la
      latencia del sistema de audio.
    - Documentar en el README la configuracion usada (dispositivo, canales, fs,
      buffer size).

    Parameters
    ----------
    signal : np.ndarray
        Senal a reproducir (1D mono o 2D ``(muestras, canales)``).
    fs : int
        Frecuencia de muestreo en Hz.
    record_duration : float
        Duracion total de la grabacion en segundos.

    Returns
    -------
    np.ndarray
        Senal grabada, con ``int(record_duration * fs)`` muestras.

    Raises
    ------
    RuntimeError
        Si no hay un dispositivo de audio disponible (con un mensaje informativo).
    """

    # Importar sounddevice dentro de la función para evitar
    # depender del hardware de audio al importar el módulo.
    import sounddevice as sd

    # Convertir la señal a un arreglo NumPy.
    signal = np.asarray(signal, dtype=np.float64)

    # Validar los parámetros de grabación.
    if fs <= 0:
        raise ValueError("La frecuencia de muestreo debe ser positiva")

    if record_duration <= 0:
        raise ValueError("La duración debe ser positiva")

    if signal.ndim not in (1, 2):
        raise ValueError("La señal debe ser mono o estéreo")

    if signal.size == 0:
        raise ValueError("La señal no puede estar vacía")

    # Calcular la duración mínima necesaria para reproducir
    # la señal completa.
    signal_duration = signal.shape[0] / fs

    if record_duration < signal_duration:
        raise ValueError("La grabación debe durar al menos lo mismo que la señal")

    # Cantidad total de muestras a grabar.
    frames = int(np.ceil(record_duration * fs))

    # Agregar silencio al final para registrar la cola
    # de reverberación de la sala.
    if signal.ndim == 1:
        playback = np.zeros(frames, dtype=np.float64)
    else:
        playback = np.zeros((frames, signal.shape[1]), dtype=np.float64)

    playback[: signal.shape[0]] = signal

    try:
        # Reproducir y grabar simultáneamente.
        recording = sd.playrec(
            playback,
            samplerate=fs,
            channels=1,
            dtype="float64",
        )

        # Esperar a que termine la operación.
        sd.wait()

    except sd.PortAudioError as error:
        raise RuntimeError(f"No se pudo acceder al dispositivo de audio: {error}") from error

    return recording
