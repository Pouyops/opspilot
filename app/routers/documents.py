from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.chunking import chunk_text
from app.db import get_session
from app.embeddings import embed_texts
from app.models import Chunk, Document
from app.schemas import DocumentCreate, DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead, status_code=201)
async def ingest_document(
    payload: DocumentCreate, session: AsyncSession = Depends(get_session)
):
    pieces = chunk_text(payload.text)
    if not pieces:
        raise HTTPException(status_code=422, detail="Document contains no text")

    vectors = await embed_texts(pieces)

    doc = Document(
        title=payload.title,
        source=payload.source,
        chunks=[
            Chunk(chunk_index=i, content=text, embedding=vec)
            for i, (text, vec) in enumerate(zip(pieces, vectors))
        ],
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc, ["created_at"])

    return DocumentRead(
        id=doc.id,
        title=doc.title,
        source=doc.source,
        created_at=doc.created_at,
        chunk_count=len(pieces),
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int, session: AsyncSession = Depends(get_session)
):
    doc = await session.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    await session.delete(doc)
    await session.commit()
