


import numpy as np
import sounddevice as sd
from app.services.audio_io import play_and_record

duration = 1.0
print("\nDispositivos de audio disponibles: ")
print(sd.query_devices())

input_device = int(input("\nNúmero de dispositivo de entrada "))
output_device = int(input("\nNúmero de dispositivo de salida "))

sd.default.device = (input_device, output_device) 

default_fs = int(
    sd.query_devices(output_device)["default_samplerate"]
)

fs = int(
    input(f"Frecuencia de muestreo en Hz [{default_fs}]: ")
    or default_fs
)
t = np.arange(fs) / fs
signal = 0.01 * np.sin(2 * np.pi * 1000 * t)
silence = np.zeros(fs)

print("Grabando señal de 1 kHz...")
recorded = play_and_record(signal, fs, 1.5).flatten()

print("Grabando ruido de fondo...")
noise = play_and_record(silence, fs, 1.5).flatten()

def rms(x):
    return np.sqrt(np.mean(x ** 2))

# Ventanas de 0.2 a 0.8 segundos
# para evitar los transitorios de inicio y final.
segment = recorded[int(0.2 * fs):int(0.8 * fs)]
noise_segment = noise[int(0.2 * fs):int(0.8 * fs)]

signal_rms = rms(segment)
noise_rms = rms(noise_segment)

# Estimación de la componente senoidal de 1 kHz
n = np.arange(len(segment))
reference = np.exp(-2j * np.pi * 1000 * n / fs)
amplitude = 2 * np.abs(np.mean(segment * reference))
tone_rms = amplitude / np.sqrt(2)

snr = 20 * np.log10(
    max(tone_rms, 1e-12) / max(noise_rms, 1e-12)
)

print()
print("RMS grabación:", signal_rms)
print("RMS ruido:", noise_rms)
print("RMS tono 1 kHz:", tone_rms)
print("SNR estimada:", round(snr, 2), "dB")
print("Clipping:", np.sum(np.abs(recorded) >= 0.999))



# ==========================================
# Medición de retardo mediante correlación
# ==========================================

print("\nMidiendo retardo del loopback...")

# Señal de prueba reproducible y no periódica
rng = np.random.default_rng(42)

# 100 ms de silencio + 200 ms de ruido de prueba
# + 700 ms de silencio
test_signal = np.zeros(fs)
start = int(0.1 * fs)
length = int(0.2 * fs)

# Ruido limitado a una amplitud segura
test_signal[start:start + length] = (
    0.01 * rng.choice([-1.0, 1.0], size=length)
)

# Reproducción y grabación simultáneas
captured = play_and_record(
    test_signal, fs, 1.5
).flatten()

# Correlación cruzada mediante FFT
from scipy.signal import correlate, correlation_lags

correlation = correlate(
    captured,
    test_signal,
    mode="full",
    method="fft"
)

lags = correlation_lags(
    len(captured),
    len(test_signal),
    mode="full"
)

# Buscar el máximo de correlación en valor absoluto
index = np.argmax(np.abs(correlation))
delay_samples = int(lags[index])
delay_ms = 1000 * delay_samples / fs

# Evaluar qué tan clara es la coincidencia
reference_energy = np.sum(test_signal ** 2)
captured_energy = np.sum(captured ** 2)
normalized_peak = (
    np.abs(correlation[index])
    / np.sqrt(reference_energy * captured_energy)
    if reference_energy > 0 and captured_energy > 0
    else 0
)

print("Retardo:", delay_samples, "muestras")
print("Retardo:", round(delay_ms, 3), "ms")
print("Correlación normalizada:", round(normalized_peak, 4))
print("Clipping en prueba de retardo:",
      np.sum(np.abs(captured) >= 0.999))


# ==========================================
# Repetibilidad del retardo: 3 mediciones
# ==========================================

print("\n--- Repetibilidad del retardo ---")

delays = []
correlations = []

for i in range(3):
    captured = play_and_record(
        test_signal, fs, 1.5
    ).flatten()

    correlation = correlate(
        captured,
        test_signal,
        mode="full",
        method="fft"
    )

    lags = correlation_lags(
        len(captured),
        len(test_signal),
        mode="full"
    )

    index = np.argmax(np.abs(correlation))
    delay_samples = int(lags[index])
    delay_ms = delay_samples * 1000 / fs

    energy = np.sum(captured ** 2)
    normalized = (
        np.abs(correlation[index])
        / np.sqrt(reference_energy * energy)
        if reference_energy > 0 and energy > 0
        else 0
    )

    delays.append(delay_ms)
    correlations.append(normalized)

    print(
        f"Medición {i + 1}: "
        f"{delay_samples} muestras | "
        f"{delay_ms:.3f} ms | "
        f"Correlación: {normalized:.3f}"
    )

print("\n--- Estadísticas ---")
print(f"Retardo promedio: {np.mean(delays):.3f} ms")
print(f"Desviación estándar: {np.std(delays, ddof=1):.3f} ms")
print(f"Retardo mínimo: {np.min(delays):.3f} ms")
print(f"Retardo máximo: {np.max(delays):.3f} ms")
print(f"Correlación promedio: {np.mean(correlations):.3f}")

