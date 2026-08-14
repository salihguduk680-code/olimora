from datetime import date
from typing import Literal

from pydantic import BaseModel


class DailyReadingResponse(BaseModel):
    reading_date: date
    main_theme: str
    relationships: str
    work_money: str
    caution: str
    source: Literal["openai", "fallback"]
    model: str | None = None
    cached: bool
    is_favorite: bool = False


class DailySignReadingResponse(DailyReadingResponse):
    sign: str
