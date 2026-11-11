from typing import Annotated

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.services.acoustic_parameters import apply_schroeder_integral, apply_smoothing
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/schroeder")
async def schroeder_endpoint(file: Annotated[UploadFile, File()]):
    try:
        with uploaded_file(file) as path:
            ir, fs = load_audio(path)
        edc = apply_schroeder_integral(ir)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    edc_json = np.nan_to_num(edc, nan=-120.0, posinf=0.0, neginf=-120.0)
    return {"sample_rate": fs, "edc_db": edc_json.tolist()}


@router.post("/smoothing")
async def smoothing_endpoint(
    file: Annotated[UploadFile, File()],
    method: Annotated[str, Form()] = "hilbert",
    window_ms: Annotated[float, Form(gt=0)] = 10.0,
):
    try:
        with uploaded_file(file) as path:
            sig, fs = load_audio(path)
        envelope = apply_smoothing(sig, fs, method=method, window_ms=window_ms)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    return {"sample_rate": fs, "method": method, "envelope": envelope.tolist()}
