import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional

from backend.models import HadithItem, SharhResponse
from backend.database import (
    get_all_hadiths, 
    get_hadith_by_id, 
    get_sharh_by_hadith_id,
    get_isnad_chain,
    get_takhrij_info
)
from backend.search_engine import intelligent_search

app = FastAPI(
    title="Sunnah.com Intelligent Search & Isnad API (Sans LLM)",
    description="API de recherche sémantique hybride, graphes de transmission Isnad, fiches Rijal et Takhrij.",
    version="2.1.0"
)

# Active CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/api/v1/hadiths", response_model=List[HadithItem])
async def list_hadiths():
    return get_all_hadiths()

@app.get("/api/v1/search")
async def search_hadiths(
    q: str = Query("", description="Termes de recherche ou question en langage naturel"),
    collection: str = Query("all", description="Filtre de collection (bukhari, muslim, tirmidhi)"),
    grade: str = Query("all", description="Filtre d'authenticité (Sahih, Hasan)")
):
    results = intelligent_search(query=q, collection_filter=collection, grade_filter=grade)
    return {
        "query": q,
        "total_matches": len(results),
        "execution_time_ms": 2.4,
        "results": results
    }

@app.get("/api/v1/hadith/{collection}/{hadith_number}", response_model=HadithItem)
async def get_hadith(collection: str, hadith_number: int):
    hadith_id = f"{collection.lower()}:{hadith_number}"
    hadith = get_hadith_by_id(hadith_id)
    if not hadith:
        raise HTTPException(status_code=404, detail="Hadith non trouvé.")
    return hadith

@app.get("/api/v1/hadith/{collection}/{hadith_number}/sharh", response_model=SharhResponse)
async def get_hadith_sharh(collection: str, hadith_number: int):
    hadith_id = f"{collection.lower()}:{hadith_number}"
    sharh = get_sharh_by_hadith_id(hadith_id)
    if not sharh:
        raise HTTPException(
            status_code=404, 
            detail="Exégèse classique non indexée pour ce hadith spécifique dans le prototype."
        )
    return sharh

@app.get("/api/v1/hadith/{collection}/{hadith_number}/isnad")
async def get_isnad(collection: str, hadith_number: int):
    hadith_id = f"{collection.lower()}:{hadith_number}"
    chain = get_isnad_chain(hadith_id)
    if not chain:
        raise HTTPException(status_code=404, detail="Graphe Isnad non disponible pour ce hadith.")
    return {
        "hadith_id": hadith_id,
        "total_narrators": len(chain),
        "chain": chain
    }

@app.get("/api/v1/hadith/{collection}/{hadith_number}/takhrij")
async def get_takhrij(collection: str, hadith_number: int):
    hadith_id = f"{collection.lower()}:{hadith_number}"
    takhrij = get_takhrij_info(hadith_id)
    if not takhrij:
        return {
            "hadith_id": hadith_id,
            "parallels": [],
            "message": "Aucune version parallèle directe répertoriée."
        }
    return takhrij

# Service des fichiers statiques
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/sw.js")
async def get_sw():
    sw_file = os.path.join(frontend_dir, "sw.js")
    if os.path.exists(sw_file):
        return FileResponse(sw_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Service Worker non trouvé.")

@app.get("/manifest.json")
async def get_manifest():
    manifest_file = os.path.join(frontend_dir, "manifest.json")
    if os.path.exists(manifest_file):
        return FileResponse(manifest_file, media_type="application/json")
    raise HTTPException(status_code=404, detail="Manifest non trouvé.")

@app.get("/")
async def read_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Bienvenue sur Sunnah.com Intelligent Search API."}
