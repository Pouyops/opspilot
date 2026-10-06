import re


def split_units(text: str) -> list[str]:
    """Break text into sentence-sized units, respecting paragraph breaks."""
    units: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        units.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip())
    return units


def chunk_text(text: str, max_chars: int = 800, overlap_chars: int = 150) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    size = 0

    for unit in split_units(text):
        if current and size + len(unit) + 1 > max_chars:
            chunks.append(" ".join(current))
            # carry the last few units into the next chunk as overlap
            tail: list[str] = []
            tail_size = 0
            for u in reversed(current):
                if tail_size + len(u) > overlap_chars:
                    break
                tail.insert(0, u)
                tail_size += len(u) + 1
            current, size = tail, tail_size

        current.append(unit)
        size += len(unit) + 1

    if current:
        chunks.append(" ".join(current))
    return chunks
