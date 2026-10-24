from fastapi import APIRouter

from app.routers.audio_http import wav_response
from app.schemas.signals import PinkNoiseRequest
from app.services.pink_noise import generate_pink_noise

router = APIRouter()


@router.post("/pink-noise")  # POST /api/v1/signals/pink-noise
async def pink_noise(req: PinkNoiseRequest):
    audio = generate_pink_noise(req.duration, req.sample_rate)
    return wav_response(audio, req.sample_rate, "pink_noise.wav")
