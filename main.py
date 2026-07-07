import os
from typing import List, Optional

import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/embeddings"
EMBED_MODEL = "openai/text-embedding-3-small"


class RankRequest(BaseModel):
    query_id: Optional[str] = None
    query: str
    candidates: List[str]


@app.get("/")
def health():
    return {"status": "ok"}


def embed_texts(texts: List[str]) -> np.ndarray:
    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": EMBED_MODEL,
            "input": texts,
            "provider": {"order": ["openai"], "allow_fallbacks": False},
        },
        timeout=60,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Embedding API error: {resp.text}")

    data = resp.json()["data"]
    data_sorted = sorted(data, key=lambda d: d["index"])
    return np.array([d["embedding"] for d in data_sorted], dtype=np.float64)


@app.post("/rank")
def rank(req: RankRequest):
    texts = [req.query] + req.candidates
    vecs = embed_texts(texts)

    query_vec = vecs[0]
    cand_vecs = vecs[1:]

    query_unit = query_vec / np.linalg.norm(query_vec)
    cand_norms = np.linalg.norm(cand_vecs, axis=1, keepdims=True)
    cand_units = cand_vecs / cand_norms

    sims = cand_units @ query_unit

    top3 = np.argsort(-sims)[:3].tolist()

    return {"ranking": top3}
