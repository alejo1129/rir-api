from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.schemas.responses import BandAnalysisResponse
from app.services.acoustic_parameters import calculate_parameters_from_ir
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/parameters", response_model=BandAnalysisResponse)
async def acoustic_parameters(
    file: Annotated[UploadFile, File()],
) -> BandAnalysisResponse:
    try:
        with uploaded_file(file) as path:
            ir, fs = load_audio(path)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err

    params = calculate_parameters_from_ir(ir, fs)

    return BandAnalysisResponse(
        sample_rate=fs,
        duration=len(ir) / fs,
        center_frequencies=[float(freq) for freq in params["EDT"]],
        parameters=params,
    )
