import numpy as np
import pytest

from app.services.acoustic_parameters import apply_schroeder_integral


@pytest.mark.parametrize(
    "ir",
    [
        np.array([]),
        np.zeros(100),
        np.ones((2, 2)),
        np.array([1.0, np.nan]),
        np.array([1.0, np.inf]),
    ],
)
def test_schroeder_invalid_input(ir):
    """Rechaza respuestas al impulso invalidas."""
    with pytest.raises(ValueError):
        apply_schroeder_integral(ir)


def test_schroeder_zero_tail():
    """Una cola sin energia debe producir menos infinito en dB."""
    ir = np.array([1.0, 0.0, 0.0])

    result = apply_schroeder_integral(ir)

    assert result[0] == pytest.approx(0.0)
    assert np.isneginf(result[1])
    assert np.isneginf(result[2])
