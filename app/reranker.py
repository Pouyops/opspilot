import asyncio
from functools import lru_cache

from fastembed.rerank.cross_encoder import TextCrossEncoder

RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"


@lru_cache
def get_reranker() -> TextCrossEncoder:
    return TextCrossEncoder(model_name=RERANK_MODEL, cache_dir=".models")


def _rerank_sync(query: str, documents: list[str]) -> list[float]:
    return [float(score) for score in get_reranker().rerank(query, documents)]


async def rerank(query: str, documents: list[str]) -> list[float]:
    return await asyncio.to_thread(_rerank_sync, query, documents)
