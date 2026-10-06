import asyncio
from functools import lru_cache

from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache
def get_model() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=".models")


def _embed_sync(texts: list[str]) -> list[list[float]]:
    return [vec.tolist() for vec in get_model().embed(texts)]


async def embed_texts(texts: list[str]) -> list[list[float]]:
    return await asyncio.to_thread(_embed_sync, texts)
