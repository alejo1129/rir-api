import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from app.services.acoustic_parameters import (
    apply_schroeder_integral,
    calculate_parameters_from_ir,
    linear_regression,
)
from app.services.filter import filter_single_band
from app.services.signal_utils import generate_synthetic_ir, load_audio

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "m3"
IMAGES = OUTPUT / "images"
AUDIO = ROOT / "docs" / "m2" / "audio"

FS = 32000
BANDS = [125, 250, 500, 1000, 2000, 4000]

# T60 objetivo por banda para la respuesta sintética.
SYNTHETIC_T60 = {
    125: 1.8,
    250: 1.7,
    500: 1.6,
    1000: 1.5,
    2000: 1.3,
    4000: 1.1,
}


def prepare_directories():
    IMAGES.mkdir(parents=True, exist_ok=True)


def create_signals():
    duration = 4.5

    synthetic_ir = generate_synthetic_ir(
        duration=duration,
        t60_values=SYNTHETIC_T60,
        fs=FS,
    )

    real_ir, real_fs = load_audio(str(AUDIO / "ri_t60_largo_stairwell.wav"))

    if real_fs != FS:
        raise ValueError(f"Frecuencia inesperada en RI real: {real_fs} Hz")

    return {
        "Sintética": (synthetic_ir, FS),
        "Escalera real": (real_ir, real_fs),
    }


def create_schroeder_plot(ir, fs):
    edc = apply_schroeder_integral(ir)
    time = np.arange(len(edc)) / fs

    mask = np.isfinite(edc) & (edc >= -35) & (edc <= -5)
    slope, intercept, r2 = linear_regression(time[mask], edc[mask])

    regression = slope * time[mask] + intercept

    plt.figure(figsize=(10, 5))
    plt.plot(time, edc, label="Curva de Schroeder")
    plt.plot(
        time[mask],
        regression,
        "--",
        label=f"Regresión lineal (R² = {r2:.4f})",
    )
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Nivel de energía (dB)")
    plt.title("Decaimiento energético e integral de Schroeder")
    plt.ylim(-60, 2)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(IMAGES / "curva_schroeder.png", dpi=160)
    plt.close()

    return slope, intercept, r2


def create_band_comparison(ir, fs, title, filename):
    plt.figure(figsize=(10, 6))

    for fc in BANDS:
        filtered = filter_single_band(ir, fs, fc)
        edc = apply_schroeder_integral(filtered)
        time = np.arange(len(edc)) / fs

        plt.plot(time, edc, label=f"{fc} Hz")

    plt.xlabel("Tiempo (s)")
    plt.ylabel("Nivel de energía (dB)")
    plt.title(title)
    plt.ylim(-60, 2)
    plt.grid(True, alpha=0.3)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(IMAGES / filename, dpi=160)
    plt.close()


def calculate_results(signals):
    rows = []

    for signal_name, (ir, fs) in signals.items():
        parameters = calculate_parameters_from_ir(ir, fs)

        for parameter_name, bands in parameters.items():
            for fc in BANDS:
                rows.append(
                    {
                        "Senal": signal_name,
                        "Banda_Hz": fc,
                        "Parametro": parameter_name,
                        "Valor": bands[fc],
                    }
                )

    with open(
        OUTPUT / "resultados_parametros.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["Senal", "Banda_Hz", "Parametro", "Valor"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return rows


def main():
    prepare_directories()
    signals = create_signals()

    synthetic_ir, synthetic_fs = signals["Sintética"]
    real_ir, real_fs = signals["Escalera real"]

    slope, intercept, r2 = create_schroeder_plot(
        synthetic_ir,
        synthetic_fs,
    )

    create_band_comparison(
        synthetic_ir,
        synthetic_fs,
        "Comparación del decaimiento por bandas - RI sintética",
        "comparacion_bandas_sintetica.png",
    )

    create_band_comparison(
        real_ir,
        real_fs,
        "Comparación del decaimiento por bandas - RI real",
        "comparacion_bandas_escalera.png",
    )

    results = calculate_results(signals)

    summary = {
        "senal": "Sintética",
        "frecuencia_muestreo_hz": synthetic_fs,
        "duracion_s": len(synthetic_ir) / synthetic_fs,
        "pendiente_db_s": slope,
        "intercepto_db": intercept,
        "R2": r2,
    }

    with open(
        OUTPUT / "validacion_schroeder.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(file, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)

    print("\n=== EVIDENCIA M3 GENERADA ===")
    print(f"Carpeta: {OUTPUT}")
    print(f"Frecuencia de muestreo: {FS} Hz")
    print(f"Pendiente Schroeder: {slope:.4f} dB/s")
    print(f"R²: {r2:.5f}")
    print("\nResultados por señal y banda:")
    for row in results:
        print(row)
    print("\nGráficos y CSV guardados correctamente.")


if __name__ == "__main__":
    main()
