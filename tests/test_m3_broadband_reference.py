"""Prueba de regresion para la referencia temporal broadband de M3."""

import numpy as np
import pytest

from app.services.acoustic_parameters import calculate_parameters_from_ir


def test_d50_c80_use_broadband_peak_across_bands(monkeypatch):
    fs = 16000

    # RI original: sonido directo en la muestra 1600.
    ir = np.zeros(8000, dtype=np.float64)
    ir[1600] = 10.0

    # Simulamos una banda cuyo maximo ocurre despues
    # del sonido directo broadband.
    def fake_filter(signal, fs, center_freq):
        band = np.zeros_like(signal, dtype=np.float64)

        # El recorte deja 5 ms antes del sonido directo.
        direct_idx = int(0.005 * fs)

        # Sonido directo.
        band[direct_idx] = 2.0

        # Reflexion a los 25 ms: dentro de D50 y C80.
        band[direct_idx + int(0.025 * fs)] = 8.0

        # Reflexion a los 100 ms: fuera de D50 y C80.
        band[direct_idx + int(0.100 * fs)] = 1.0

        return band

    monkeypatch.setattr(
        "app.services.acoustic_parameters.filter_single_band",
        fake_filter,
    )

    results = calculate_parameters_from_ir(ir, fs)

    # Energias: directo = 4, reflexion temprana = 64,
    # reflexion tardia = 1.
    expected_d50 = (68.0 / 69.0) * 100.0
    expected_c80 = 10.0 * np.log10(68.0 / 1.0)

    for fc in (125, 250, 500, 1000, 2000, 4000):
        assert results["D50"][fc] == pytest.approx(expected_d50)
        assert results["C80"][fc] == pytest.approx(expected_c80)
