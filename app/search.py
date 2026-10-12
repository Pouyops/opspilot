from sqlalchemy import RowMapping, text

import re

from app.db import SessionLocal
from app.embeddings import embed_texts

RRF_K = 60
CANDIDATES = 50


async def search_chunks(query: str, limit: int = 5) -> list[dict]:
    (query_vector,) = await embed_texts([query])

    stmt = text(
        """
        WITH semantic AS (
            SELECT c.id, c.document_id, c.content,
                   ROW_NUMBER() OVER (ORDER BY c.embedding <=> :vector) AS rank
            FROM chunks c
            ORDER BY c.embedding <=> :vector
            LIMIT :candidates
        ),
        keyword AS (
            SELECT c.id, c.document_id, c.content,
                   ROW_NUMBER() OVER (ORDER BY ts_rank(c.tsv, to_tsquery('english', :tsq)) DESC) AS rank
            FROM chunks c
            WHERE c.tsv @@ to_tsquery('english', :tsq)
            ORDER BY ts_rank(c.tsv, to_tsquery('english', :tsq)) DESC
            LIMIT :candidates
        )
        SELECT COALESCE(s.document_id, k.document_id) AS document_id,
               COALESCE(s.content, k.content)             AS content,
               1.0 / (:rrf_k + s.rank) AS semantic_score,
               1.0 / (:rrf_k + k.rank) AS keyword_score,
               COALESCE(1.0 / (:rrf_k + s.rank), 0.0)
                   + COALESCE(1.0 / (:rrf_k + k.rank), 0.0) AS score
        FROM semantic s
        FULL OUTER JOIN keyword k ON k.id = s.id
        ORDER BY score DESC
        LIMIT :limit
        """
    )
    words = re.findall(r"\w+", query.lower())
    params = {
        "vector": str(query_vector),
        "tsq": " | ".join(words),
        "candidates": CANDIDATES,
        "rrf_k": RRF_K,
        "limit": limit,
    }

    async with SessionLocal() as session:
        rows: list[RowMapping] = (await session.execute(stmt, params)).mappings().all()

    return [
    {
        "document_id": row["document_id"],
        "content": row["content"],
        "semantic_score": float(row["semantic_score"] or 0.0),
        "keyword_score": float(row["keyword_score"] or 0.0),
        "score": float(row["score"]),
    }
    for row in rows
]
