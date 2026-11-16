from enum import StrEnum

from pydantic import BaseModel


class SmoothingMethod(StrEnum):
    HILBERT = "hilbert"
    MOVING_AVERAGE = "moving_average"


class SmoothingResponse(BaseModel):
    method: SmoothingMethod
    window_ms: float
    sample_rate: int
    time_step: float
    envelope: list[float]


class SchroederResponse(BaseModel):
    sample_rate: int
    num_samples: int
    lundeby_applied: bool = False
    time_step: float
    edc_db: list[float]
