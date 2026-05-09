from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class WineBase(BaseModel):
    name: str
    varietal: str
    producer: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    vintage: Optional[int] = Field(None, ge=1800, le=2100)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    notes: Optional[str] = None
    date_tried: Optional[date] = None
    price: Optional[float] = Field(None, ge=0)


class WineCreate(WineBase):
    pass


class WineUpdate(BaseModel):
    name: Optional[str] = None
    varietal: Optional[str] = None
    producer: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    vintage: Optional[int] = Field(None, ge=1800, le=2100)
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    notes: Optional[str] = None
    date_tried: Optional[date] = None
    price: Optional[float] = Field(None, ge=0)


class Wine(WineBase):
    id: int

    model_config = {"from_attributes": True}


class Suggestion(BaseModel):
    name: str
    varietal: str
    region: str
    country: str
    description: str
    reason: str
    estimated_price_range: str
