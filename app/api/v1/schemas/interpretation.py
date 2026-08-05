from typing import Literal

from pydantic import BaseModel, Field

from app.api.v1.schemas.natal_chart import NatalChartPreviewRequest


class AthenaInterpretationRequest(NatalChartPreviewRequest):
    name: str = Field(default="Gökyüzü Yolcusu", min_length=1, max_length=80)


class AthenaInterpretationResponse(BaseModel):
    interpretation: str
    source: Literal["openai", "fallback"]
    model: str | None = None
