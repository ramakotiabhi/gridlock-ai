"""
GridLock AI — RAG Retrieval API Server
=======================================
FastAPI server exposing IBM Docling + FAISS retrieval for the frontend.
Run: python rag_server.py
Serves on: http://localhost:8001
"""

import os
import json
import pickle
from typing import Optional
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠ Run: pip install fastapi uvicorn")

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    RETRIEVAL_AVAILABLE = True
except ImportError:
    RETRIEVAL_AVAILABLE = False

# ── Fallback knowledge base (no FAISS needed) ─────────────────────
FALLBACK_REGULATIONS = [
    {
        "id": "art_48_12",
        "article": "Article 48.12",
        "text": "Any car that has been lapped by the leader will be required to pass the cars on the lead lap and the Safety Car when the clerk of the course decides it is safe to do so. ALL lapped cars must pass before the Safety Car returns to the pit lane.",
        "source": "FIA Formula 1 Sporting Regulations 2021",
        "relevance_tags": ["safety car", "lapped cars", "unlapping", "abu dhabi"]
    },
    {
        "id": "art_39_4",
        "article": "Article 39.4",
        "text": "Any manoeuvre likely to hinder another driver, such as deliberate braking when not required for safety or another obvious reason, is prohibited. Sudden, unexpected deceleration in front of a following car constitutes dangerous driving.",
        "source": "FIA Formula 1 Sporting Regulations 2021",
        "relevance_tags": ["braking", "dangerous driving", "jeddah", "deliberate", "hinder"]
    },
    {
        "id": "driving_standards_overlap",
        "article": "GCB Guideline 1 — Driving Standards",
        "text": "A driver is entitled to racing room alongside a competitor at a corner if the car is sufficiently alongside at the apex. 'Sufficiently alongside' is generally interpreted as 50% or more car-length overlap at the apex of the corner.",
        "source": "FIA Driving Standards Guidelines 2021",
        "relevance_tags": ["overlap", "racing room", "corner", "silverstone", "copse"]
    },
    {
        "id": "art_57_1",
        "article": "Article 57.1 / 57.3",
        "text": "If a race is suspended and cannot be restarted, results will be taken at the end of the penultimate lap. Half-points will be awarded if less than 75% of the race distance has been completed but more than 2 laps have been completed.",
        "source": "FIA Formula 1 Sporting Regulations 2021",
        "relevance_tags": ["half points", "red flag", "suspended race", "belgium", "rain"]
    },
    {
        "id": "art_55_5",
        "article": "Article 55.5",
        "text": "Cars must not be released into the path of oncoming traffic. An unsafe release occurs when a car exits its pit stop position with insufficient gap to oncoming pit lane traffic to avoid a collision or dangerous situation.",
        "source": "FIA Formula 1 Sporting Regulations 2021",
        "relevance_tags": ["unsafe release", "pit lane", "monaco", "gap"]
    },
    {
        "id": "art_38_3",
        "article": "Article 38.3",
        "text": "A driver may not force another driver off the track. Responsibility for braking distances in wet conditions is heightened. Drivers must account for reduced grip and increased stopping distances when braking late at corners.",
        "source": "FIA Formula 1 Sporting Regulations 2021",
        "relevance_tags": ["wet conditions", "braking", "hungary", "collision", "responsibility"]
    }
]


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="GridLock AI — RAG Server",
        description="IBM Docling + FAISS retrieval API for FIA regulation search",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"]
    )

    class RetrievalRequest(BaseModel):
        query: str
        top_k: int = 5
        incident_id: Optional[str] = None

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "faiss_available": RETRIEVAL_AVAILABLE,
            "fallback_regulations": len(FALLBACK_REGULATIONS),
            "index_path": str(Path("./gridlock_index").exists())
        }

    @app.post("/retrieve")
    async def retrieve(req: RetrievalRequest):
        """Retrieve relevant FIA regulation passages for a given query."""
        if RETRIEVAL_AVAILABLE and Path("./gridlock_index/regulations.faiss").exists():
            try:
                index = faiss.read_index("./gridlock_index/regulations.faiss")
                with open("./gridlock_index/chunks.pkl", "rb") as f:
                    chunks = pickle.load(f)
                model = SentenceTransformer('all-MiniLM-L6-v2')
                q_emb = model.encode([req.query]).astype('float32')
                distances, indices = index.search(q_emb, req.top_k)
                results = [{"text": chunks[i], "score": float(distances[0][j])}
                           for j, i in enumerate(indices[0]) if i < len(chunks)]
                return {"results": results, "source": "faiss_index", "count": len(results)}
            except Exception as e:
                pass  # Fall through to fallback

        # Fallback: keyword-based matching
        query_lower = req.query.lower()
        scored = []
        for reg in FALLBACK_REGULATIONS:
            score = sum(1 for tag in reg["relevance_tags"] if tag in query_lower)
            if score > 0:
                scored.append((score, reg))
        scored.sort(reverse=True, key=lambda x: x[0])
        results = [{"text": f"[{r['article']}] {r['text']} | Source: {r['source']}", "score": s}
                   for s, r in scored[:req.top_k]] or \
                  [{"text": f"[{r['article']}] {r['text']}", "score": 0}
                   for r in FALLBACK_REGULATIONS[:req.top_k]]

        return {"results": results, "source": "fallback_knowledge_base", "count": len(results)}

    @app.get("/regulations")
    async def list_regulations():
        """List all pre-loaded regulation articles."""
        return {"regulations": FALLBACK_REGULATIONS, "count": len(FALLBACK_REGULATIONS)}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
else:
    if __name__ == "__main__":
        print("FastAPI not available. Run: pip install fastapi uvicorn")
