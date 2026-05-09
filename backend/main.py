from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import wines, suggestions, local_recommendations

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wine Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wines.router, prefix="/api/wines", tags=["wines"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["suggestions"])
app.include_router(
    local_recommendations.router,
    prefix="/api/local-recommendations",
    tags=["local-recommendations"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
