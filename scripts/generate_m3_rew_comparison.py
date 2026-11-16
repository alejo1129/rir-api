import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
M3_DIR = ROOT / "docs" / "m3"
IMAGES_DIR = M3_DIR / "images"

RIR_RESULTS = M3_DIR / "resultados_parametros.csv"
REW_RESULTS = M3_DIR / "rew_stairwell_rt60.txt"
OUTPUT_CSV = M3_DIR / "comparacion_rew.csv"
OUTPUT_FIGURE = IMAGES_DIR / "validacion_vs_rew_t30.png"

BANDS = [125, 250, 500, 1000, 2000, 4000]
PARAMETERS = ["EDT", "T20", "T30", "C80"]


def load_rir_results() -> dict[tuple[str, int], float]:
    results = {}

    with RIR_RESULTS.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["Senal"] != "Escalera real":
                continue

            parameter = row["Parametro"]
            band = int(float(row["Banda_Hz"]))

            if parameter not in PARAMETERS or band not in BANDS:
                continue

            value = row["Valor"].strip()
            if value:
                results[(parameter, band)] = float(value)

    return results


def load_rew_results() -> dict[tuple[str, int], float]:
    results = {}

    for line in REW_RESULTS.read_text(encoding="utf-8").splitlines():
        parts = line.split()

        if len(parts) < 10:
            continue

        try:
            band = int(float(parts[0]))
        except ValueError:
            continue

        if band not in BANDS or parts[1] != "1/1":
            continue

        results[("EDT", band)] = float(parts[2])
        results[("T20", band)] = float(parts[4])
        results[("T30", band)] = float(parts[6])

        # Las ultimas cuatro columnas de REW son C50, C80, D50 y TS.
        results[("C80", band)] = float(parts[-3])

    return results


def time_tolerance(reference: float) -> float:
    return min(abs(reference) * 0.10, 0.5)


def create_comparison(
    rir_results: dict[tuple[str, int], float],
    rew_results: dict[tuple[str, int], float],
) -> list[dict[str, str | int | float]]:
    rows = []

    for parameter in PARAMETERS:
        for band in BANDS:
            key = (parameter, band)

            if key not in rir_results:
                raise ValueError(f"Falta {parameter} de RIR-API para la banda de {band} Hz")

            if key not in rew_results:
                raise ValueError(f"Falta {parameter} de REW para la banda de {band} Hz")

            rir_value = rir_results[key]
            rew_value = rew_results[key]
            difference = abs(rir_value - rew_value)

            if parameter == "C80":
                tolerance = 1.0
                relative_error = ""
                unit = "dB"
                passes = difference <= tolerance
            else:
                tolerance = time_tolerance(rew_value)
                relative_error = difference / abs(rew_value) * 100
                unit = "s"
                passes = difference <= tolerance

            rows.append(
                {
                    "Parametro": parameter,
                    "Banda_Hz": band,
                    "RIR_API": rir_value,
                    "REW": rew_value,
                    "Diferencia_abs": difference,
                    "Error_relativo_pct": relative_error,
                    "Tolerancia_abs": tolerance,
                    "Unidad": unit,
                    "Cumple": "SI" if passes else "NO",
                }
            )

    return rows


def save_comparison(rows: list[dict[str, str | int | float]]) -> None:
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Parametro",
                "Banda_Hz",
                "RIR_API",
                "REW",
                "Diferencia_abs",
                "Error_relativo_pct",
                "Tolerancia_abs",
                "Unidad",
                "Cumple",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def create_validation_figure(
    rir_results: dict[tuple[str, int], float],
    rew_results: dict[tuple[str, int], float],
) -> None:
    x = list(range(len(BANDS)))

    rir_t30 = [rir_results[("T30", band)] for band in BANDS]
    rew_t30 = [rew_results[("T30", band)] for band in BANDS]
    tolerances = [time_tolerance(value) for value in rew_t30]

    lower = [
        reference - tolerance for reference, tolerance in zip(rew_t30, tolerances, strict=True)
    ]
    upper = [
        reference + tolerance for reference, tolerance in zip(rew_t30, tolerances, strict=True)
    ]

    plt.figure(figsize=(10, 6))

    plt.fill_between(
        x,
        lower,
        upper,
        alpha=0.2,
        label="Tolerancia de aceptacion",
    )

    plt.plot(
        x,
        rew_t30,
        marker="o",
        label="REW",
    )

    plt.plot(
        x,
        rir_t30,
        marker="o",
        label="RIR-API",
    )

    plt.xticks(x, [str(band) for band in BANDS])
    plt.xlabel("Banda de octava (Hz)")
    plt.ylabel("T30 (s)")
    plt.title("Validacion T30 por banda - RIR-API vs REW")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_FIGURE, dpi=160)
    plt.close()


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    rir_results = load_rir_results()
    rew_results = load_rew_results()

    rows = create_comparison(rir_results, rew_results)

    save_comparison(rows)
    create_validation_figure(rir_results, rew_results)

    passed = sum(row["Cumple"] == "SI" for row in rows)
    failed = len(rows) - passed

    print()
    print("=== VALIDACION RIR-API VS REW ===")
    print(f"Comparaciones: {len(rows)}")
    print(f"Dentro de tolerancia: {passed}")
    print(f"Fuera de tolerancia: {failed}")

    if failed:
        print()
        print("Resultados fuera de tolerancia:")

        for row in rows:
            if row["Cumple"] == "NO":
                print(
                    f"{row['Parametro']} {row['Banda_Hz']} Hz: "
                    f"RIR-API={row['RIR_API']:.3f}, "
                    f"REW={row['REW']:.3f}, "
                    f"diferencia={row['Diferencia_abs']:.3f} {row['Unidad']}"
                )

    print()
    print(f"CSV: {OUTPUT_CSV}")
    print(f"Grafico: {OUTPUT_FIGURE}")


if __name__ == "__main__":
    main()
