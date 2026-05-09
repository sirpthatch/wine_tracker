import asyncio
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.geocoder import geocode_address
from ..services.store_finder import find_wine_stores
from ..services.scraper import scrape_store_inventory

router = APIRouter()

# How many stores to scrape concurrently (keeps wall-clock latency reasonable)
_MAX_CONCURRENT_SCRAPES = 4


@router.post("/", response_model=schemas.LocalRecommendationsResponse)
async def get_local_recommendations(
    req: schemas.LocalRecommendationsRequest,
    db: Session = Depends(get_db),
):
    # 1. Geocode
    geo = await geocode_address(req.address)
    if not geo:
        raise HTTPException(
            status_code=422,
            detail="Could not locate that address. Try adding a city or zip code.",
        )

    lat, lon = geo["lat"], geo["lon"]

    # 2. Find nearby wine stores via OpenStreetMap Overpass
    raw_stores = await find_wine_stores(lat, lon, req.radius_m)

    # 3. Build preference profile from the user's highest-rated wines
    user_wines = db.query(models.Wine).all()
    liked = [w for w in user_wines if w.rating and w.rating >= 4.0]
    top_varietals: set[str] = {
        v for v, _ in Counter(w.varietal for w in liked).most_common(5)
    }
    top_regions: set[str] = {
        r
        for r, _ in Counter(w.region for w in liked if w.region).most_common(3)
    }

    # 4. Scrape stores concurrently (cap at _MAX_CONCURRENT_SCRAPES)
    semaphore = asyncio.Semaphore(_MAX_CONCURRENT_SCRAPES)

    async def process(raw: dict) -> schemas.NearbyStore:
        async with semaphore:
            raw_inventory, status = await scrape_store_inventory(raw.get("website") or "")

        inventory = [
            schemas.ScrapedWine(
                name=item["name"],
                varietal=item.get("varietal"),
                vintage=item.get("vintage"),
                price=item.get("price"),
                match_reason=_match_reason(item, top_varietals, top_regions),
            )
            for item in raw_inventory
        ]

        # Bubble matched wines to top
        inventory.sort(key=lambda w: (w.match_reason is None))

        return schemas.NearbyStore(
            name=raw["name"],
            address=raw["address"],
            website=raw.get("website"),
            phone=raw.get("phone"),
            distance_m=raw["distance_m"],
            walking_minutes=raw["walking_minutes"],
            inventory=inventory,
            inventory_status=status,
        )

    stores = await asyncio.gather(*[process(s) for s in raw_stores])

    return schemas.LocalRecommendationsResponse(
        geocoded_address=geo["display_name"],
        stores=list(stores),
    )


def _match_reason(
    item: dict, top_varietals: set[str], top_regions: set[str]
) -> str | None:
    varietal = item.get("varietal") or ""
    name_lower = item.get("name", "").lower()

    reasons: list[str] = []

    if varietal and varietal in top_varietals:
        reasons.append(f"matches your preferred varietal ({varietal})")

    for region in top_regions:
        if region.lower() in name_lower:
            reasons.append(f"from a region you enjoy ({region})")
            break

    return reasons[0].capitalize() if reasons else None
