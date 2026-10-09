
"""
RIR-API - Milestone 1: Generación de señales.

Router HTTP para la generación de señales de medición acústica.

Implementa el endpoint POST /api/v1/signals/sine-sweep,
que permite generar un barrido senoidal logarítmico (ESS)
mediante el método de Farina (2000).

El barrido generado se devuelve como archivo WAV para su
utilización en mediciones de respuesta al impulso.

Referencia:
Farina, A. (2000). Simultaneous measurement of impulse
response and distortion with a swept-sine technique.
108th AES Convention.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.sine_sweep import generate_sine_sweep_pair
from app.routers.audio_http import wav_response

router = APIRouter()


class SineSweepRequest(BaseModel):
    duration: float = 5.0
    f1: float = 20.0
    f2: float = 20000.0
    fs: int = 44100


@router.post("/sine-sweep")
def create_sine_sweep(params: SineSweepRequest):
    try:
        sweep, inverse_filter = generate_sine_sweep_pair(
            duration=params.duration,
            f1=params.f1,
            f2=params.f2,
            fs=params.fs,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return wav_response(
        signal=sweep,
        fs=params.fs,
        filename="sine_sweep.wav",
    )


