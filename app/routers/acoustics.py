from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.services.acoustic_parameters import calculate_parameters_from_ir
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/parameters")
async def acoustic_parameters(file: Annotated[UploadFile, File()]):
    try:
        with uploaded_file(file) as path:
            ir, fs = load_audio(path)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    params = calculate_parameters_from_ir(ir, fs)
    return {
        param: {str(freq): float(val) for freq, val in bands.items()}
        for param, bands in params.items()
    }
