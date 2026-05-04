from pydantic import BaseModel, Field, field_validator
from typing import List, Union, Optional
import numpy as np


class PixelArrayData(BaseModel):
    pixels: Union[List[List[float]], List[float], List[int]]

    @field_validator("pixels")
    @classmethod
    def validate_pixels(cls, v):
        if not v:
            raise ValueError("Canvas pixel data cannot be empty")
        if isinstance(v[0], (int, float)):
            flat_len = len(v)
        elif isinstance(v[0], list):
            flat_len = len(v) * len(v[0])
        else:
            raise ValueError("Invalid pixel data format")
        if flat_len != 784:
            raise ValueError(f"Canvas must contain exactly 784 pixels (28x28), got {flat_len}")
        return v

    def to_normalized_array(self) -> np.ndarray:
        arr = np.array(self.pixels, dtype=np.float64)
        if arr.ndim == 2:
            arr = arr.flatten()
        return arr / 255.0 if arr.max() > 1.0 else arr


class PredictRequest(BaseModel):
    canvas: PixelArrayData


class TrainRequest(BaseModel):
    canvas: PixelArrayData
    label: int = Field(..., ge=0, le=9)


class ModelUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    accuracy_log: Optional[float] = Field(None, ge=0.0, le=1.0)


class PredictResponse(BaseModel):
    prediction: int
    confidence: float
    model_version: str


class TrainResponse(BaseModel):
    status: str
    model_version: str
    message: str
