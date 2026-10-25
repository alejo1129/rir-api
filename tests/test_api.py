import io

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from app.main import app
from app.routers.audio_http import wav_response

client = TestClient(app)

xfail_m2 = pytest.mark.xfail(strict=False, reason="se implementa en M2")
xfail_m3 = pytest.mark.xfail(strict=False, reason="se implementa en M3")


def _wav_en_memoria(signal: np.ndarray, fs: int) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, signal, fs, format="WAV", subtype="PCM_16")
    return buffer.getvalue()


def _ri_sintetica(fs: int = 44100, t60: float = 0.5) -> np.ndarray:
    t = np.arange(fs) / fs
    rng = np.random.default_rng(0)
    ir = rng.standard_normal(fs) * np.exp(-3 * np.log(10) / t60 * t)
    return ir / np.max(np.abs(ir)) * 0.9


class TestHealthEndpoint:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    def test_root_returns_200(self):
        assert client.get("/").status_code == 200

    def test_root_returns_api_info(self):
        data = client.get("/").json()
        assert data["name"] == "RIR-API"
        assert "docs" in data


def test_wav_response_roundtrip():
    senal = np.linspace(-0.5, 0.5, 1000)
    response = wav_response(senal, 8000)
    assert response.media_type == "audio/wav"
    leida, fs = sf.read(io.BytesIO(response.body))
    assert fs == 8000
    assert np.allclose(leida, senal, atol=1e-6)


# M1 - Endpoints (Ya sin xfail porque están andando perfecto)


def test_signals_pink_noise_endpoint():
    response = client.post(
        "/api/v1/signals/pink-noise", json={"duration": 1.0, "sample_rate": 44100}
    )
    assert response.status_code == 200
    senal, fs = sf.read(io.BytesIO(response.content))
    assert fs == 44100
    assert len(senal) == 44100


def test_signals_sine_sweep_endpoint():
    pedido = {"duration": 1.0, "start_freq": 20, "end_freq": 20000, "sample_rate": 44100}
    sweep = client.post("/api/v1/signals/sine-sweep", json=pedido)
    inverso = client.post("/api/v1/signals/sine-sweep", json={**pedido, "inverse": True})
    assert sweep.status_code == 200 and inverso.status_code == 200
    s, fs = sf.read(io.BytesIO(sweep.content))
    k, _ = sf.read(io.BytesIO(inverso.content))
    assert fs == 44100
    assert len(s) == 44100
    assert not np.allclose(s[: len(k)], k[: len(s)])


def test_invalid_duration_returns_422():
    response = client.post(
        "/api/v1/signals/pink-noise", json={"duration": -1.0, "sample_rate": 44100}
    )
    assert response.status_code == 422


# M2


@xfail_m2
def test_signals_synthetic_ir_endpoint():
    pedido = {"duration": 1.0, "t60_values": {"1000": 0.8}, "sample_rate": 44100}
    response = client.post("/api/v1/signals/synthetic-ir", json=pedido)
    assert response.status_code == 200
    senal, fs = sf.read(io.BytesIO(response.content))
    assert fs == 44100
    assert len(senal) == 44100


@xfail_m2
def test_filters_single_band_endpoint():
    fs = 44100
    ruido = np.random.default_rng(1).standard_normal(fs) * 0.5
    archivos = {"file": ("ruido.wav", _wav_en_memoria(ruido, fs), "audio/wav")}
    response = client.post(
        "/api/v1/filters/single-band", files=archivos, data={"center_freq": 1000}
    )
    assert response.status_code == 200
    filtrada, fs_out = sf.read(io.BytesIO(response.content))
    assert fs_out == fs
    assert len(filtrada) == fs


@xfail_m2
def test_invalid_file_returns_422():
    archivos = {"file": ("no_es_audio.wav", b"esto no es audio", "audio/wav")}
    response = client.post(
        "/api/v1/filters/single-band", files=archivos, data={"center_freq": 1000}
    )
    assert response.status_code == 422


# M3


@xfail_m3
def test_acoustics_parameters_endpoint():
    fs = 44100
    archivos = {"file": ("ir.wav", _wav_en_memoria(_ri_sintetica(fs), fs), "audio/wav")}
    response = client.post("/api/v1/acoustics/parameters", files=archivos)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@xfail_m3
def test_utils_schroeder_endpoint():
    fs = 44100
    archivos = {"file": ("ir.wav", _wav_en_memoria(_ri_sintetica(fs), fs), "audio/wav")}
    response = client.post("/api/v1/utils/schroeder", files=archivos)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


@xfail_m3
def test_utils_smoothing_endpoint():
    fs = 44100
    archivos = {"file": ("ir.wav", _wav_en_memoria(_ri_sintetica(fs), fs), "audio/wav")}
    response = client.post("/api/v1/utils/smoothing", files=archivos)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
