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


# --- Local recommendations ---------------------------------------------------

class LocalRecommendationsRequest(BaseModel):
    address: str
    radius_m: int = Field(default=800, ge=100, le=5000)


class ScrapedWine(BaseModel):
    name: str
    varietal: Optional[str] = None
    vintage: Optional[str] = None
    price: Optional[str] = None
    match_reason: Optional[str] = None


class NearbyStore(BaseModel):
    name: str
    address: str
    website: Optional[str] = None
    phone: Optional[str] = None
    distance_m: int
    walking_minutes: int
    inventory: list[ScrapedWine] = []
    inventory_status: str = "Not checked"


class LocalRecommendationsResponse(BaseModel):
    geocoded_address: str
    stores: list[NearbyStore]
