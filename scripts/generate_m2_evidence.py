import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, correlate, correlation_lags, fftconvolve, sosfilt

from app.services.filter import filter_single_band
from app.services.signal_utils import generate_synthetic_ir, get_impulse_response
from app.services.sine_sweep import generate_sine_sweep_pair


def main() -> None:
    sample_rate = 44100
    target_t60 = 0.8
    center_frequency = 1000.0
    duration = 3 * target_t60

    # Generar la respuesta al impulso sintética.
    impulse_response = generate_synthetic_ir(
        duration=duration,
        t60_values={center_frequency: target_t60},
        fs=sample_rate,
    )

    # Analizar la banda de 1000 Hz.
    filtered_signal = filter_single_band(
        impulse_response,
        sample_rate,
        center_frequency,
    )

    # Calcular la integral de Schroeder (energía acumulada hacia atrás).
    energy = np.cumsum(filtered_signal[::-1] ** 2)[::-1]
    energy = energy / energy[0]
    energy_db = 10 * np.log10(np.maximum(energy, 1e-12))

    time = np.arange(len(energy_db)) / sample_rate

    # Estimar T60 mediante regresión entre -5 y -25 dB.
    mask = (energy_db <= -5) & (energy_db >= -25)
    slope, intercept = np.polyfit(time[mask], energy_db[mask], 1)
    estimated_t60 = -60 / slope

    # Crear los gráficos.
    figure, axes = plt.subplots(2, 1, figsize=(11, 8))

    axes[0].plot(time, impulse_response, linewidth=0.5)
    axes[0].set_title("Respuesta al impulso sintética")
    axes[0].set_xlabel("Tiempo (s)")
    axes[0].set_ylabel("Amplitud")
    axes[0].grid(True)

    axes[1].plot(time, energy_db, label="Curva de decaimiento")
    axes[1].plot(
        time[mask],
        slope * time[mask] + intercept,
        "--",
        label="Regresión lineal (-5 a -25 dB)",
    )
    axes[1].axhline(-60, color="gray", linestyle=":")
    axes[1].axvline(target_t60, color="red", linestyle=":", label="T60 objetivo")
    axes[1].set_title("Curva de decaimiento energético (Schroeder)")
    axes[1].set_xlabel("Tiempo (s)")
    axes[1].set_ylabel("Nivel relativo (dB)")
    axes[1].set_ylim(-80, 5)
    axes[1].grid(True)
    axes[1].legend()

    figure.suptitle(
        f"Banda de {center_frequency:.0f} Hz | "
        f"T60 objetivo: {target_t60:.2f} s | "
        f"T60 estimado: {estimated_t60:.2f} s"
    )
    figure.tight_layout()

    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "docs" / "m2" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "ri_sintetica_t60.png"
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)

    print(f"T60 objetivo: {target_t60:.3f} s")
    print(f"T60 estimado: {estimated_t60:.3f} s")
    print(f"Gráfico guardado en: {output_path}")
    generate_deconvolution_plot()
    generate_filter_plot()


def generate_deconvolution_plot() -> None:
    sample_rate = 44100
    rng = np.random.default_rng(0)

    # Crear una respuesta al impulso de referencia.
    n_samples = int(0.5 * sample_rate)
    time = np.arange(n_samples) / sample_rate

    reference_ir = 0.3 * rng.standard_normal(n_samples) * np.exp(-3 * np.log(10) / 0.3 * time)
    reference_ir[0] = 1.0

    # Limitar la respuesta al impulso al rango de frecuencias de interés.
    sos = butter(
        2,
        [100, 10000],
        btype="bandpass",
        fs=sample_rate,
        output="sos",
    )
    reference_ir = sosfilt(sos, reference_ir)

    # Generar el barrido senoidal y su filtro inverso.
    sweep, inverse_filter = generate_sine_sweep_pair(
        2.0,
        20,
        20000,
        sample_rate,
    )

    # Simular la grabación del barrido atravesando el sistema.
    recording = fftconvolve(sweep, reference_ir, mode="full")

    # Recuperar la respuesta al impulso mediante deconvolución.
    recovered_ir = get_impulse_response(recording, inverse_filter)

    # Alinear ambas señales para compararlas.
    correlation = correlate(recovered_ir, reference_ir, mode="full")
    lags = correlation_lags(
        len(recovered_ir),
        len(reference_ir),
        mode="full",
    )
    lag = int(lags[np.argmax(correlation)])

    if lag >= 0:
        recovered_aligned = recovered_ir[lag:]
        reference_aligned = reference_ir[: len(recovered_aligned)]
    else:
        reference_aligned = reference_ir[-lag:]
        recovered_aligned = recovered_ir[: len(reference_aligned)]

    common_length = min(len(reference_aligned), len(recovered_aligned))
    reference_aligned = reference_aligned[:common_length]
    recovered_aligned = recovered_aligned[:common_length]

    # Normalizar ambas señales para facilitar la comparación.
    reference_aligned = reference_aligned / np.max(np.abs(reference_aligned))
    recovered_aligned = recovered_aligned / np.max(np.abs(recovered_aligned))

    similarity = np.corrcoef(reference_aligned, recovered_aligned)[0, 1]

    plot_time = np.arange(common_length) / sample_rate

    figure, axis = plt.subplots(figsize=(11, 5))
    axis.plot(plot_time, reference_aligned, label="RI de referencia", linewidth=1)
    axis.plot(
        plot_time,
        recovered_aligned,
        label="RI recuperada por deconvolución",
        alpha=0.75,
        linewidth=1,
    )
    axis.set_title(f"Deconvolución mediante sine sweep | Correlación: {similarity:.4f}")
    axis.set_xlabel("Tiempo (s)")
    axis.set_ylabel("Amplitud normalizada")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()

    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "docs" / "m2" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "deconvolucion.png"
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)

    print(f"Correlación entre RI original y recuperada: {similarity:.4f}")
    print(f"Gráfico guardado en: {output_path}")


def generate_filter_plot() -> None:
    sample_rate = 44100
    center_frequency = 1000.0

    # Crear un impulso unitario centrado en el tiempo.
    impulse = np.zeros(sample_rate)
    impulse[sample_rate // 2] = 1.0

    # Aplicar el filtro de banda de octava.
    filtered_signal = filter_single_band(
        impulse,
        sample_rate,
        center_frequency,
    )

    # Obtener la respuesta en frecuencia mediante FFT.
    spectrum = np.abs(np.fft.rfft(filtered_signal))
    frequencies = np.fft.rfftfreq(len(filtered_signal), 1 / sample_rate)

    # Normalizar y convertir a decibeles.
    spectrum_db = 20 * np.log10(np.maximum(spectrum / np.max(spectrum), 1e-12))

    # Frecuencias que queremos comprobar.
    lower_edge = center_frequency / np.sqrt(2)
    upper_edge = center_frequency * np.sqrt(2)
    test_frequencies = [
        center_frequency / 2,
        lower_edge,
        center_frequency,
        upper_edge,
        center_frequency * 2,
    ]

    measured_values = np.interp(
        np.log10(test_frequencies),
        np.log10(frequencies[1:]),
        spectrum_db[1:],
    )

    # Graficar la respuesta en frecuencia.
    figure, axis = plt.subplots(figsize=(11, 6))
    axis.plot(frequencies[1:], spectrum_db[1:], linewidth=1.5)

    axis.axvline(lower_edge, color="gray", linestyle="--", label="Límite inferior")
    axis.axvline(center_frequency, color="red", linestyle=":", label="Centro: 1000 Hz")
    axis.axvline(upper_edge, color="gray", linestyle="--", label="Límite superior")

    axis.set_xscale("log")
    axis.set_xlim(100, 10000)
    axis.set_ylim(-100, 5)
    axis.set_title("Respuesta en frecuencia - Filtro de banda de octava")
    axis.set_xlabel("Frecuencia (Hz)")
    axis.set_ylabel("Magnitud (dB)")
    axis.grid(True, which="both")
    axis.legend()
    figure.tight_layout()

    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "docs" / "m2" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "filtro_octava_1000hz.png"
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)

    print("\nRespuesta del filtro:")
    for frequency, value in zip(test_frequencies, measured_values, strict=True):
        print(f"  {frequency:8.2f} Hz: {value:7.2f} dB")

    print(f"Gráfico guardado en: {output_path}")


if __name__ == "__main__":
    main()
