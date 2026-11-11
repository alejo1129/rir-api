from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal as sps

from app.services.pink_noise import generate_pink_noise
from app.services.sine_sweep import generate_sine_sweep_pair

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "docs" / "m1"


def generate_pink_noise_plot() -> None:
    """Genera la validacion espectral del ruido rosa."""
    fs = 44100
    duration = 10.0

    noise = generate_pink_noise(duration, fs)

    frequencies, psd = sps.welch(noise, fs=fs, nperseg=8192)
    psd_db = 10 * np.log10(np.maximum(psd, 1e-20))

    band = (frequencies >= 100) & (frequencies <= 10000)

    slope, intercept = np.polyfit(
        np.log2(frequencies[band]),
        psd_db[band],
        1,
    )

    fitted_psd = slope * np.log2(frequencies[band]) + intercept

    figure, axis = plt.subplots(figsize=(10, 5))

    valid = frequencies > 0

    axis.semilogx(
        frequencies[valid],
        psd_db[valid],
        label="PSD del ruido rosa",
    )

    axis.semilogx(
        frequencies[band],
        fitted_psd,
        linestyle="--",
        label=f"Pendiente = {slope:.2f} dB/oct",
    )

    axis.set_title("Validacion espectral del ruido rosa")
    axis.set_xlabel("Frecuencia [Hz]")
    axis.set_ylabel("PSD [dB]")
    axis.grid(True, which="both")
    axis.legend()

    figure.tight_layout()

    output_path = OUTPUT_DIR / "pink_noise_spectrum.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    print(f"Ruido rosa: pendiente = {slope:.2f} dB/oct")
    print(f"Imagen: {output_path}")


def generate_sweep_spectrogram() -> None:
    """Genera el espectrograma del sine sweep."""
    fs = 44100
    duration = 5.0
    f1 = 20.0
    f2 = 20000.0

    sweep, _ = generate_sine_sweep_pair(
        duration,
        f1,
        f2,
        fs,
    )

    frequencies, times, spectrum = sps.spectrogram(
        sweep,
        fs=fs,
        nperseg=4096,
        noverlap=2048,
    )

    spectrum_db = 10 * np.log10(np.maximum(spectrum, 1e-20))

    figure, axis = plt.subplots(figsize=(10, 5))

    mesh = axis.pcolormesh(
        times,
        frequencies,
        spectrum_db,
        shading="auto",
    )

    axis.set_yscale("log")
    axis.set_ylim(f1, f2)

    axis.set_title("Espectrograma del sine sweep")
    axis.set_xlabel("Tiempo [s]")
    axis.set_ylabel("Frecuencia [Hz]")

    figure.colorbar(mesh, ax=axis, label="Nivel [dB]")

    figure.tight_layout()

    output_path = OUTPUT_DIR / "sine_sweep_spectrogram.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    print(f"Sweep: {f1:.0f} Hz -> {f2:.0f} Hz")
    print(f"Imagen: {output_path}")


def generate_sweep_inverse_plot() -> None:
    """Valida la convolucion entre el sweep y su filtro inverso."""
    fs = 44100

    sweep, inverse_filter = generate_sine_sweep_pair(
        5.0,
        20.0,
        20000.0,
        fs,
    )

    impulse = sps.fftconvolve(sweep, inverse_filter)

    energy = impulse**2
    peak_index = int(np.argmax(energy))

    excluded_window = int(0.01 * fs)

    rest = np.concatenate(
        [
            energy[: peak_index - excluded_window],
            energy[peak_index + excluded_window :],
        ]
    )

    peak_to_rest_db = 10 * np.log10(energy[peak_index] / np.mean(rest))

    normalized = np.abs(impulse) / np.max(np.abs(impulse))
    impulse_db = 20 * np.log10(np.maximum(normalized, 1e-6))

    time = (np.arange(len(impulse)) - peak_index) / fs

    visible = (time >= -0.05) & (time <= 0.05)

    figure, axis = plt.subplots(figsize=(10, 5))

    axis.plot(
        time[visible] * 1000,
        impulse_db[visible],
    )

    axis.set_ylim(-120, 5)

    axis.set_title(f"Convolucion sweep x filtro inverso (pico/resto = {peak_to_rest_db:.1f} dB)")
    axis.set_xlabel("Tiempo respecto del pico [ms]")
    axis.set_ylabel("Nivel normalizado [dB]")
    axis.grid(True)

    figure.tight_layout()

    output_path = OUTPUT_DIR / "sweep_inverse_convolution.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)

    print(f"Sweep x inverso: pico/resto = {peak_to_rest_db:.1f} dB")
    print(f"Imagen: {output_path}")


def main() -> None:
    """Genera las evidencias graficas faltantes de M1."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generate_pink_noise_plot()
    generate_sweep_spectrogram()
    generate_sweep_inverse_plot()


if __name__ == "__main__":
    main()
