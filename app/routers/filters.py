from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file, wav_response
from app.services.filter import filter_single_band
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/single-band")
async def single_band_filter(
    file: Annotated[UploadFile, File()],
    center_freq: Annotated[float, Form(gt=0)],
):
    try:
        with uploaded_file(file) as path:
            signal, fs = load_audio(path)
        filtered = filter_single_band(signal, fs, center_freq)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    return wav_response(filtered, fs, "filtered.wav")

