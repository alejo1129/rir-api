from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import soundfile as sf

from app.services.audio_io import play_and_record
from app.services.sine_sweep import generate_sine_sweep_pair

FS = 48000
SWEEP_DURATION = 5.0
RECORD_DURATION = 7.0
INPUT_DEVICE = 1
OUTPUT_DEVICE = 3
SWEEP_LEVEL = 0.1

OUTPUT_DIR = Path("docs/m1")
WAV_PATH = OUTPUT_DIR / "qa_play_and_record_real.wav"
TXT_PATH = OUTPUT_DIR / "qa_play_and_record_real.txt"
PNG_PATH = OUTPUT_DIR / "qa_play_and_record_real.png"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sd.default.device = (INPUT_DEVICE, OUTPUT_DEVICE)
    sd.default.blocksize = 0

    input_info = sd.query_devices(INPUT_DEVICE)
    output_info = sd.query_devices(OUTPUT_DEVICE)

    sd.check_input_settings(
        device=INPUT_DEVICE,
        channels=1,
        samplerate=FS,
    )
    sd.check_output_settings(
        device=OUTPUT_DEVICE,
        channels=2,
        samplerate=FS,
    )

    sweep, _ = generate_sine_sweep_pair(
        SWEEP_DURATION,
        20,
        20000,
        FS,
    )

    sweep = SWEEP_LEVEL * sweep

    # Reproducir el mismo sweep por ambos canales de salida.
    stereo_sweep = np.column_stack((sweep, sweep))

    print("Configuracion de la prueba")
    print("--------------------------")
    print(f"Entrada: {input_info['name']}")
    print(f"Salida: {output_info['name']}")
    print(f"Frecuencia de muestreo: {FS} Hz")
    print(f"Blocksize: {sd.default.blocksize}")
    print(f"Duracion sweep: {SWEEP_DURATION} s")
    print(f"Duracion grabacion: {RECORD_DURATION} s")
    print(f"Nivel digital sweep: {SWEEP_LEVEL}")
    print()
    print("Reproduciendo sweep y grabando...")

    recorded = play_and_record(
        stereo_sweep,
        FS,
        RECORD_DURATION,
    )

    recorded = np.asarray(recorded, dtype=np.float64).squeeze()

    peak = float(np.max(np.abs(recorded)))
    rms = float(np.sqrt(np.mean(recorded**2)))

    peak_dbfs = float(20 * np.log10(max(peak, 1e-12)))
    rms_dbfs = float(20 * np.log10(max(rms, 1e-12)))

    clipped_samples = int(np.count_nonzero(np.abs(recorded) >= 0.999))

    sf.write(WAV_PATH, recorded, FS, subtype="PCM_24")

    report = (
        "Validacion real de play_and_record\n"
        "===================================\n"
        f"Entrada: {input_info['name']}\n"
        f"Salida: {output_info['name']}\n"
        f"Canales de entrada usados: 1\n"
        f"Canales de salida usados: 2\n"
        f"Frecuencia de muestreo: {FS} Hz\n"
        f"Blocksize: {sd.default.blocksize} (automatico / PortAudio)\n"
        f"Duracion sweep: {SWEEP_DURATION} s\n"
        f"Duracion grabacion: {RECORD_DURATION} s\n"
        f"Pre-roll: 0.5 s\n"
        f"Nivel digital sweep: {SWEEP_LEVEL}\n"
        f"Muestras grabadas: {len(recorded)}\n"
        f"Pico: {peak:.9f}\n"
        f"Pico: {peak_dbfs:.2f} dBFS\n"
        f"RMS: {rms:.9f}\n"
        f"RMS: {rms_dbfs:.2f} dBFS\n"
        f"Muestras con clipping: {clipped_samples}\n"
    )

    TXT_PATH.write_text(report, encoding="utf-8")

    t = np.arange(len(recorded)) / FS

    plt.figure(figsize=(12, 5))
    plt.plot(t, recorded, linewidth=0.7)
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Amplitud")
    plt.title("Validacion real de play_and_record con sine sweep")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=150)
    plt.close()

    print()
    print(report)
    print(f"WAV guardado en: {WAV_PATH}")
    print(f"Reporte guardado en: {TXT_PATH}")
    print(f"Grafico guardado en: {PNG_PATH}")


if __name__ == "__main__":
    main()
