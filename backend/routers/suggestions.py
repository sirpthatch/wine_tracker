from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import Counter
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

WINE_CATALOG: List[dict] = [
    # Cabernet Sauvignon
    {"name": "Stag's Leap Wine Cellars Cask 23", "varietal": "Cabernet Sauvignon", "region": "Napa Valley", "country": "USA", "description": "One of Napa's most iconic Cabs, famous from the 1976 Paris Tasting.", "estimated_price_range": "$200–$300"},
    {"name": "Opus One", "varietal": "Cabernet Sauvignon Blend", "region": "Napa Valley", "country": "USA", "description": "A legendary Napa Bordeaux-style blend by Mondavi and Rothschild.", "estimated_price_range": "$300–$400"},
    {"name": "Jordan Cabernet Sauvignon", "varietal": "Cabernet Sauvignon", "region": "Sonoma County", "country": "USA", "description": "Approachable Sonoma Cab with classic structure and elegance.", "estimated_price_range": "$50–$70"},
    {"name": "Chateau Montelena Estate", "varietal": "Cabernet Sauvignon", "region": "Napa Valley", "country": "USA", "description": "Historic Napa estate with powerful, age-worthy Cabernets.", "estimated_price_range": "$80–$120"},
    {"name": "Shafer Hillside Select", "varietal": "Cabernet Sauvignon", "region": "Napa Valley", "country": "USA", "description": "Rich, concentrated Stags Leap Cab from a single hillside vineyard.", "estimated_price_range": "$300–$400"},
    # Merlot / Bordeaux
    {"name": "Chateau Petrus", "varietal": "Merlot", "region": "Pomerol, Bordeaux", "country": "France", "description": "The world's most celebrated Merlot-based wine.", "estimated_price_range": "$3,000+"},
    {"name": "Duckhorn Three Palms Merlot", "varietal": "Merlot", "region": "Napa Valley", "country": "USA", "description": "America's most awarded Merlot, lush and structured.", "estimated_price_range": "$80–$100"},
    {"name": "Chateau Leoville-Las Cases", "varietal": "Cabernet Sauvignon Blend", "region": "Saint-Julien, Bordeaux", "country": "France", "description": "Super Second from Saint-Julien, known for its Pauillac-like power.", "estimated_price_range": "$150–$250"},
    # Pinot Noir
    {"name": "Domaine de la Romanee-Conti La Tache", "varietal": "Pinot Noir", "region": "Burgundy", "country": "France", "description": "One of the world's greatest Pinot Noirs, ethereal complexity.", "estimated_price_range": "$5,000+"},
    {"name": "Domaine Leroy Chambolle-Musigny", "varietal": "Pinot Noir", "region": "Burgundy", "country": "France", "description": "Biodynamic Burgundy of extraordinary purity and depth.", "estimated_price_range": "$500–$800"},
    {"name": "Kosta Browne Gap's Crown", "varietal": "Pinot Noir", "region": "Petaluma Gap, Sonoma", "country": "USA", "description": "Cult California Pinot with intense fruit and silky texture.", "estimated_price_range": "$80–$120"},
    {"name": "Adelsheim Ribbon Ridge Pinot Noir", "varietal": "Pinot Noir", "region": "Willamette Valley, Oregon", "country": "USA", "description": "Elegant Oregon Pinot with bright acidity and red fruit.", "estimated_price_range": "$40–$60"},
    {"name": "Elk Cove Pinot Noir", "varietal": "Pinot Noir", "region": "Willamette Valley, Oregon", "country": "USA", "description": "Pioneer Oregon estate delivering Burgundian-style Pinot Noir.", "estimated_price_range": "$30–$50"},
    {"name": "Felton Road Block 3 Pinot Noir", "varietal": "Pinot Noir", "region": "Central Otago", "country": "New Zealand", "description": "Benchmark Central Otago Pinot with pristine fruit and minerality.", "estimated_price_range": "$60–$90"},
    # Chardonnay
    {"name": "Domaine Leflaive Puligny-Montrachet", "varietal": "Chardonnay", "region": "Burgundy", "country": "France", "description": "White Burgundy perfection — mineral, precise, and profound.", "estimated_price_range": "$150–$250"},
    {"name": "Peter Michael Mon Plaisir Chardonnay", "varietal": "Chardonnay", "region": "Knights Valley, Sonoma", "country": "USA", "description": "Burgundian-inspired California Chardonnay of great elegance.", "estimated_price_range": "$80–$120"},
    {"name": "Kongsgaard Chardonnay", "varietal": "Chardonnay", "region": "Napa Valley", "country": "USA", "description": "Full-bodied, textured Napa Chardonnay with great complexity.", "estimated_price_range": "$100–$150"},
    {"name": "Domaine Ramonet Chassagne-Montrachet", "varietal": "Chardonnay", "region": "Burgundy", "country": "France", "description": "Rich and nutty white Burgundy from a legendary estate.", "estimated_price_range": "$100–$200"},
    # Italian reds
    {"name": "Gaja Barbaresco", "varietal": "Nebbiolo", "region": "Piedmont", "country": "Italy", "description": "Angelo Gaja's benchmark Barbaresco — powerful and aromatic.", "estimated_price_range": "$200–$300"},
    {"name": "Barolo Monfortino - Giacomo Conterno", "varietal": "Nebbiolo", "region": "Piedmont", "country": "Italy", "description": "Italy's most revered Barolo, released only in outstanding vintages.", "estimated_price_range": "$500+"},
    {"name": "Sassicaia", "varietal": "Cabernet Sauvignon Blend", "region": "Tuscany", "country": "Italy", "description": "The original Super Tuscan that changed Italian winemaking.", "estimated_price_range": "$150–$250"},
    {"name": "Ornellaia", "varietal": "Cabernet Sauvignon Blend", "region": "Tuscany", "country": "Italy", "description": "Lush, structured Super Tuscan with extraordinary depth.", "estimated_price_range": "$200–$300"},
    {"name": "Biondi-Santi Brunello di Montalcino", "varietal": "Sangiovese", "region": "Tuscany", "country": "Italy", "description": "The historic estate that created Brunello di Montalcino.", "estimated_price_range": "$200–$400"},
    {"name": "Giacomo Conterno Barbera d'Asti", "varietal": "Barbera", "region": "Piedmont", "country": "Italy", "description": "Deep, vibrant Barbera with rare complexity from a Barolo master.", "estimated_price_range": "$30–$50"},
    # Spanish
    {"name": "Vega Sicilia Unico", "varietal": "Tempranillo Blend", "region": "Ribera del Duero", "country": "Spain", "description": "Spain's most prestigious wine, aged decades before release.", "estimated_price_range": "$400+"},
    {"name": "Alvaro Palacios L'Ermita", "varietal": "Grenache", "region": "Priorat", "country": "Spain", "description": "Spain's rarest Grenache, from century-old bush vines.", "estimated_price_range": "$500+"},
    {"name": "La Rioja Alta Gran Reserva 904", "varietal": "Tempranillo", "region": "Rioja", "country": "Spain", "description": "Traditional Rioja Gran Reserva with silky tannins and elegance.", "estimated_price_range": "$40–$60"},
    {"name": "Bodegas Muga Prado Enea Gran Reserva", "varietal": "Tempranillo Blend", "region": "Rioja", "country": "Spain", "description": "Classic, oak-aged Rioja Gran Reserva of great complexity.", "estimated_price_range": "$60–$90"},
    # Syrah / Rhone
    {"name": "E. Guigal Cote-Rotie La Mouline", "varietal": "Syrah", "region": "Rhone Valley", "country": "France", "description": "One of the world's greatest Syrahs, from 100+ year old vines.", "estimated_price_range": "$300–$500"},
    {"name": "Chapoutier Ermitage Le Pavillon", "varietal": "Syrah", "region": "Hermitage, Rhone", "country": "France", "description": "Brooding, mineral Northern Rhone Syrah of extraordinary density.", "estimated_price_range": "$200–$400"},
    {"name": "Penfolds Grange", "varietal": "Shiraz", "region": "South Australia", "country": "Australia", "description": "Australia's greatest wine — a multi-regional Shiraz icon.", "estimated_price_range": "$700–$1,000"},
    {"name": "Two Hands Brave Faces Shiraz", "varietal": "Shiraz", "region": "McLaren Vale", "country": "Australia", "description": "Rich, spicy McLaren Vale Shiraz with lush fruit and dark chocolate.", "estimated_price_range": "$25–$40"},
    # White wines beyond Chardonnay
    {"name": "Trimbach Clos Sainte Hune Riesling", "varietal": "Riesling", "region": "Alsace", "country": "France", "description": "The benchmark Alsatian Riesling — dry, mineral, and profound.", "estimated_price_range": "$150–$250"},
    {"name": "Mosel Wehlener Sonnenuhr Auslese - JJ Prum", "varietal": "Riesling", "region": "Mosel", "country": "Germany", "description": "Elegant, sweet-edged Mosel Riesling with ethereal floral notes.", "estimated_price_range": "$80–$120"},
    {"name": "Chateau d'Yquem", "varietal": "Semillon Blend", "region": "Sauternes, Bordeaux", "country": "France", "description": "The world's greatest dessert wine, lusciously complex.", "estimated_price_range": "$300–$500"},
    {"name": "Domaine Weinbach Clos des Capucins Gewurztraminer", "varietal": "Gewurztraminer", "region": "Alsace", "country": "France", "description": "Aromatic, spicy Alsatian Gewurz with exceptional depth.", "estimated_price_range": "$40–$60"},
    {"name": "Cloudy Bay Sauvignon Blanc", "varietal": "Sauvignon Blanc", "region": "Marlborough", "country": "New Zealand", "description": "The iconic Marlborough Sauvignon Blanc that launched a category.", "estimated_price_range": "$20–$30"},
    {"name": "Didier Dagueneau Pouilly-Fume Silex", "varietal": "Sauvignon Blanc", "region": "Loire Valley", "country": "France", "description": "Flintily mineral Loire Sauvignon that rivals the greatest whites.", "estimated_price_range": "$80–$130"},
]

VARIETAL_SIBLINGS: dict[str, list[str]] = {
    "Cabernet Sauvignon": ["Cabernet Sauvignon Blend", "Merlot", "Cabernet Franc", "Bordeaux Blend"],
    "Cabernet Sauvignon Blend": ["Cabernet Sauvignon", "Merlot", "Cabernet Franc"],
    "Merlot": ["Cabernet Sauvignon", "Cabernet Sauvignon Blend", "Cabernet Franc"],
    "Pinot Noir": ["Burgundy", "Nebbiolo"],
    "Nebbiolo": ["Pinot Noir", "Barbera"],
    "Barbera": ["Nebbiolo", "Sangiovese"],
    "Sangiovese": ["Barbera", "Nebbiolo"],
    "Syrah": ["Shiraz", "Grenache"],
    "Shiraz": ["Syrah", "Grenache"],
    "Grenache": ["Syrah", "Shiraz", "Tempranillo"],
    "Tempranillo": ["Grenache", "Tempranillo Blend"],
    "Tempranillo Blend": ["Tempranillo", "Grenache"],
    "Chardonnay": ["White Burgundy", "Chablis"],
    "Riesling": ["Gewurztraminer"],
    "Gewurztraminer": ["Riesling"],
    "Sauvignon Blanc": ["Semillon Blend"],
    "Semillon Blend": ["Sauvignon Blanc", "Chardonnay"],
}


@router.get("/", response_model=List[schemas.Suggestion])
def get_suggestions(db: Session = Depends(get_db)):
    wines = db.query(models.Wine).all()

    tried_names = {w.name.lower() for w in wines}

    liked_wines = [w for w in wines if w.rating and w.rating >= 4.0]

    varietal_counts: Counter = Counter()
    region_counts: Counter = Counter()

    for wine in liked_wines:
        varietal_counts[wine.varietal] += 1
        if wine.region:
            region_counts[wine.region] += 1

    top_varietals = {v for v, _ in varietal_counts.most_common(3)}
    related_varietals: set[str] = set()
    for v in top_varietals:
        related_varietals.update(VARIETAL_SIBLINGS.get(v, []))
    all_liked_varietals = top_varietals | related_varietals

    top_regions = {r for r, _ in region_counts.most_common(3)}

    suggestions: list[schemas.Suggestion] = []

    for wine in WINE_CATALOG:
        if wine["name"].lower() in tried_names:
            continue

        reason_parts: list[str] = []

        if wine["varietal"] in top_varietals:
            reason_parts.append(f"matches your top varietal ({wine['varietal']})")
        elif wine["varietal"] in related_varietals:
            reason_parts.append(f"similar to varietals you love ({wine['varietal']})")

        if any(r.lower() in wine["region"].lower() for r in top_regions):
            reason_parts.append(f"from a region you enjoy ({wine['region']})")

        if reason_parts:
            suggestions.append(
                schemas.Suggestion(
                    name=wine["name"],
                    varietal=wine["varietal"],
                    region=wine["region"],
                    country=wine["country"],
                    description=wine["description"],
                    reason=", ".join(reason_parts).capitalize(),
                    estimated_price_range=wine["estimated_price_range"],
                )
            )

    # If no personalized suggestions (not enough data), return a curated starter list
    if not suggestions:
        starters = [
            "Jordan Cabernet Sauvignon",
            "Elk Cove Pinot Noir",
            "Adelsheim Ribbon Ridge Pinot Noir",
            "Two Hands Brave Faces Shiraz",
            "Cloudy Bay Sauvignon Blanc",
            "La Rioja Alta Gran Reserva 904",
        ]
        for wine in WINE_CATALOG:
            if wine["name"] in starters and wine["name"].lower() not in tried_names:
                suggestions.append(
                    schemas.Suggestion(
                        name=wine["name"],
                        varietal=wine["varietal"],
                        region=wine["region"],
                        country=wine["country"],
                        description=wine["description"],
                        reason="A great wine to start exploring",
                        estimated_price_range=wine["estimated_price_range"],
                    )
                )

    return suggestions[:10]
