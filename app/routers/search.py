from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.search import MIN_RERANK_SCORE, search_chunks
from app.db import get_session
from app.models import Document
from app.search import search_chunks

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search(
    q: str = Query(min_length=1),
    limit: int = Query(5, ge=1, le=20),
    min_score: float = Query(MIN_RERANK_SCORE),
    session: AsyncSession = Depends(get_session),
) -> dict:
    hits = await search_chunks(q, limit=limit, min_score=min_score)

    doc_ids = [hit["document_id"] for hit in hits]
    titles = {}
    if doc_ids:
        result = await session.execute(
            select(Document.id, Document.title, Document.source).where(
                Document.id.in_(doc_ids)
            )
        )
        for doc_id, title, source in result.all():
            titles[doc_id] = (title, source)

    results = []
    for hit in hits:
        title, source = titles.get(hit["document_id"], (None, None))
        results.append(
            {
                "document_id": hit["document_id"],
                "title": title,
                "source": source,
                "content": hit["content"],
                "score": round(hit["score"], 6),
                "semantic_score": round(hit["semantic_score"], 6),
                "keyword_score": round(hit["keyword_score"], 6),
		"rerank_score": round(hit["rerank_score"],4),
            }
        )

    return {"query": q, "count": len(results), "results": results}
