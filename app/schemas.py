from datetime import datetime

from pydantic import BaseModel, Field


class FileSummary(BaseModel):
    id: int
    filename: str
    min_depth: float
    max_depth: float
    curves: list[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True


class CurveSeriesResponse(BaseModel):
    depth: list[float]
    curves: dict[str, list[float | None]]


class InterpretRequest(BaseModel):
    curves: list[str] = Field(default_factory=list)
    start_depth: float | None = None
    end_depth: float | None = None


class ChatRequest(BaseModel):
    message: str
    curves: list[str] = Field(default_factory=list)
    start_depth: float | None = None
    end_depth: float | None = None
