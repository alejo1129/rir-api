import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "docs" / "m3" / "images"
IMAGES.mkdir(parents=True, exist_ok=True)

FS = 32000
BANDS = [125, 250, 500, 1000, 2000, 4000]

# 1. Respuesta en frecuencia de los filtros implementados en filter.py
fig, ax = plt.subplots(figsize=(11, 6))

for fc in BANDS:
    f_low = fc / np.sqrt(2.0)
    f_high = fc * np.sqrt(2.0)

    sos = signal.butter(
        N=4,
        Wn=[f_low, f_high],
        btype="bandpass",
        fs=FS,
        output="sos",
    )

    frequencies, response = signal.sosfreqz(sos, worN=8192, fs=FS)
    magnitude_db = 20 * np.log10(np.maximum(np.abs(response), 1e-12))

    ax.plot(frequencies, magnitude_db, label=f"{fc} Hz")

ax.set_xscale("log")
ax.set_xlim(50, 12000)
ax.set_ylim(-100, 5)
ax.set_xlabel("Frecuencia (Hz)")
ax.set_ylabel("Magnitud (dB)")
ax.set_title("Respuesta en frecuencia de los filtros Butterworth por banda")
ax.grid(True, which="both", alpha=0.3)
ax.legend(title="Banda central")
fig.tight_layout()
fig.savefig(IMAGES / "comparacion_filtros_bandas.png", dpi=180)
plt.close(fig)

# 2. Comparación T30: RIR-API contra REW
csv_path = ROOT / "docs" / "m3" / "comparacion_rew.csv"

with csv_path.open(encoding="utf-8", newline="") as file:
    rows = [row for row in csv.DictReader(file) if row["Parametro"] == "T30"]

rows.sort(key=lambda row: int(row["Banda_Hz"]))

x = np.arange(len(rows))
bands = [row["Banda_Hz"] for row in rows]
api = np.array([float(row["RIR_API"]) for row in rows])
rew = np.array([float(row["REW"]) for row in rows])
tolerance = np.array([float(row["Tolerancia_abs"]) for row in rows])
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(x, api, marker="o", linewidth=2, label="RIR-API")
ax.plot(x, rew, marker="s", linewidth=2, label="REW")
ax.fill_between(
    x,
    rew - tolerance,
    rew + tolerance,
    alpha=0.2,
    label="Tolerancia de REW",
)

ax.set_xticks(x)
ax.set_xticklabels(bands)
ax.set_xlabel("Banda de octava (Hz)")
ax.set_ylabel("T30 (s)")
ax.set_title("Validación de T30: RIR-API vs. REW (Stairwell)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(IMAGES / "validacion_vs_rew_t30.png", dpi=180)
plt.close(fig)

print("Gráficos generados correctamente:")
print(IMAGES / "comparacion_filtros_bandas.png")
print(IMAGES / "validacion_vs_rew_t30.png")
