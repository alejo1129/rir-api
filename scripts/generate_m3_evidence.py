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

SYNTHETIC_T60 = {
    125: 1.8,
    250: 1.7,
    500: 1.6,
    1000: 1.5,
    2000: 1.3,
    4000: 1.1,
}


def prepare_directories() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)


def create_signals() -> dict[str, tuple[np.ndarray, int]]:
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
        "Sintetica": (synthetic_ir, FS),
        "Escalera real": (real_ir, real_fs),
    }


def regression_for_range(
    time: np.ndarray,
    edc: np.ndarray,
    db_start: float,
    db_end: float,
) -> tuple[np.ndarray, np.ndarray, float, float, float]:
    mask = np.isfinite(edc) & (edc <= db_start) & (edc >= db_end)

    slope, intercept, r2 = linear_regression(time[mask], edc[mask])
    regression = slope * time[mask] + intercept

    return time[mask], regression, slope, intercept, r2


def create_decay_regression_plot(
    ir: np.ndarray,
    fs: int,
    center_freq: float = 1000,
) -> list[dict[str, float | str]]:
    filtered = filter_single_band(ir, fs, center_freq)
    edc = apply_schroeder_integral(filtered)
    time = np.arange(len(edc)) / fs

    ranges = {
        "EDT": (0.0, -10.0),
        "T20": (-5.0, -25.0),
        "T30": (-5.0, -35.0),
    }

    rows = []

    plt.figure(figsize=(10, 6))
    plt.plot(time, edc, label=f"Schroeder - {center_freq:.0f} Hz")

    for name, (db_start, db_end) in ranges.items():
        fit_time, regression, slope, intercept, r2 = regression_for_range(
            time,
            edc,
            db_start,
            db_end,
        )

        plt.plot(
            fit_time,
            regression,
            "--",
            label=f"{name}: {db_start:.0f} a {db_end:.0f} dB (R²={r2:.4f})",
        )

        rows.append(
            {
                "Ajuste": name,
                "Banda_Hz": center_freq,
                "Inicio_dB": db_start,
                "Fin_dB": db_end,
                "Pendiente_dB_s": slope,
                "Intercepto_dB": intercept,
                "R2": r2,
            }
        )

    plt.xlabel("Tiempo (s)")
    plt.ylabel("Nivel de energia (dB)")
    plt.title("Curva de decaimiento y regresiones - RI sintetica, banda de 1000 Hz")
    plt.ylim(-60, 2)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(IMAGES / "curva_schroeder_regresiones.png", dpi=160)
    plt.close()

    return rows


def create_filter_comparison(fs: int) -> None:
    num_samples = 65536

    impulse = np.zeros(num_samples, dtype=np.float64)
    impulse[num_samples // 2] = 1.0

    frequencies = np.fft.rfftfreq(num_samples, d=1 / fs)

    plt.figure(figsize=(10, 6))

    for center_freq in BANDS:
        filtered = filter_single_band(impulse, fs, center_freq)

        magnitude = np.abs(np.fft.rfft(filtered))
        maximum = np.max(magnitude)

        if maximum > 0:
            magnitude = magnitude / maximum

        magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12))

        plt.semilogx(
            frequencies,
            magnitude_db,
            label=f"{center_freq} Hz",
        )

    plt.xlabel("Frecuencia (Hz)")
    plt.ylabel("Magnitud normalizada (dB)")
    plt.title("Comparacion de filtros por banda de octava")
    plt.xlim(50, 8000)
    plt.ylim(-80, 3)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(IMAGES / "comparacion_filtros_bandas.png", dpi=160)
    plt.close()


def create_band_decay_comparison(
    ir: np.ndarray,
    fs: int,
    title: str,
    filename: str,
) -> None:
    plt.figure(figsize=(10, 6))

    for center_freq in BANDS:
        filtered = filter_single_band(ir, fs, center_freq)
        edc = apply_schroeder_integral(filtered)
        time = np.arange(len(edc)) / fs

        plt.plot(time, edc, label=f"{center_freq} Hz")

    plt.xlabel("Tiempo (s)")
    plt.ylabel("Nivel de energia (dB)")
    plt.title(title)
    plt.ylim(-60, 2)
    plt.grid(True, alpha=0.3)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(IMAGES / filename, dpi=160)
    plt.close()


def calculate_results(
    signals: dict[str, tuple[np.ndarray, int]],
) -> list[dict[str, str | float | None]]:
    rows = []

    for signal_name, (ir, fs) in signals.items():
        parameters = calculate_parameters_from_ir(ir, fs)

        for parameter_name, bands in parameters.items():
            for center_freq in BANDS:
                rows.append(
                    {
                        "Senal": signal_name,
                        "Banda_Hz": center_freq,
                        "Parametro": parameter_name,
                        "Valor": bands[center_freq],
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


def create_synthetic_validation(
    rows: list[dict[str, str | float | None]],
) -> list[dict[str, float]]:
    validation_rows = []

    for center_freq in BANDS:
        t30 = next(
            row["Valor"]
            for row in rows
            if row["Senal"] == "Sintetica"
            and row["Banda_Hz"] == center_freq
            and row["Parametro"] == "T30"
        )

        if t30 is None:
            raise ValueError(f"No se pudo calcular T30 para la banda de {center_freq} Hz")

        target = SYNTHETIC_T60[center_freq]
        error_percent = abs(float(t30) - target) / target * 100

        validation_rows.append(
            {
                "Banda_Hz": center_freq,
                "T60_objetivo_s": target,
                "T30_RIR_API_s": float(t30),
                "Error_relativo_pct": error_percent,
            }
        )

    with open(
        OUTPUT / "validacion_sintetica.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Banda_Hz",
                "T60_objetivo_s",
                "T30_RIR_API_s",
                "Error_relativo_pct",
            ],
        )
        writer.writeheader()
        writer.writerows(validation_rows)

    return validation_rows


def save_regression_results(
    rows: list[dict[str, float | str]],
) -> None:
    with open(
        OUTPUT / "validacion_schroeder.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Ajuste",
                "Banda_Hz",
                "Inicio_dB",
                "Fin_dB",
                "Pendiente_dB_s",
                "Intercepto_dB",
                "R2",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    prepare_directories()

    signals = create_signals()

    synthetic_ir, synthetic_fs = signals["Sintetica"]
    real_ir, real_fs = signals["Escalera real"]

    regression_rows = create_decay_regression_plot(
        synthetic_ir,
        synthetic_fs,
    )
    save_regression_results(regression_rows)

    create_filter_comparison(FS)

    create_band_decay_comparison(
        synthetic_ir,
        synthetic_fs,
        "Comparacion del decaimiento por bandas - RI sintetica",
        "comparacion_bandas_sintetica.png",
    )

    create_band_decay_comparison(
        real_ir,
        real_fs,
        "Comparacion del decaimiento por bandas - RI real",
        "comparacion_bandas_escalera.png",
    )

    results = calculate_results(signals)
    validation_rows = create_synthetic_validation(results)

    print()
    print("=== EVIDENCIA M3 GENERADA ===")
    print(f"Carpeta: {OUTPUT}")
    print(f"Frecuencia de muestreo: {FS} Hz")

    print()
    print("Regresiones:")
    for row in regression_rows:
        print(f"{row['Ajuste']}: pendiente={row['Pendiente_dB_s']:.4f} dB/s, R2={row['R2']:.5f}")

    print()
    print("Validacion sintetica:")
    for row in validation_rows:
        print(
            f"{row['Banda_Hz']:.0f} Hz: objetivo={row['T60_objetivo_s']:.3f} s, "
            f"T30={row['T30_RIR_API_s']:.3f} s, "
            f"error={row['Error_relativo_pct']:.2f}%"
        )

    print()
    print("Graficos y CSV guardados correctamente.")


if __name__ == "__main__":
    main()
