from pydantic import BaseModel


class BandAnalysisResponse(BaseModel):
    sample_rate: int
    duration: float
    center_frequencies: list[float]
    parameters: dict[str, dict[float, float | None]]
