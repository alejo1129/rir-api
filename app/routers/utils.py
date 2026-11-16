from typing import Annotated

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.schemas.utils import SchroederResponse, SmoothingMethod, SmoothingResponse
from app.services.acoustic_parameters import apply_schroeder_integral, apply_smoothing
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/schroeder", response_model=SchroederResponse)
async def schroeder_endpoint(
    file: Annotated[UploadFile, File()],
) -> SchroederResponse:
    try:
        with uploaded_file(file) as path:
            ir, fs = load_audio(path)

        edc = apply_schroeder_integral(ir)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    edc_json = np.nan_to_num(
        edc,
        nan=-150.0,
        posinf=0.0,
        neginf=-150.0,
    )
    edc_json = np.maximum(edc_json, -150.0)

    step = max(1, round(fs / 1000))
    edc_decimated = edc_json[::step]

    return SchroederResponse(
        sample_rate=fs,
        num_samples=len(ir),
        lundeby_applied=False,
        time_step=step / fs,
        edc_db=edc_decimated.tolist(),
    )


@router.post("/smoothing", response_model=SmoothingResponse)
async def smoothing_endpoint(
    file: Annotated[UploadFile, File()],
    method: Annotated[SmoothingMethod, Form()] = SmoothingMethod.HILBERT,
    window_ms: Annotated[float, Form(gt=0, le=100)] = 10.0,
) -> SmoothingResponse:
    try:
        with uploaded_file(file) as path:
            sig, fs = load_audio(path)

        envelope = apply_smoothing(
            sig,
            fs,
            method=method.value,
            window_ms=window_ms,
        )
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    step = max(1, round(fs / 1000))
    envelope_decimated = envelope[::step]

    return SmoothingResponse(
        method=method,
        window_ms=window_ms,
        sample_rate=fs,
        time_step=step / fs,
        envelope=envelope_decimated.tolist(),
    )
