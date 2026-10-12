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
HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*#*\s*$")


def split_sections(text: str) -> list[tuple[list[str], str]]:
    """Return (heading path, body) pairs, one per section of the page."""
    sections: list[tuple[list[str], str]] = []
    stack: list[tuple[int, str]] = []
    body: list[str] = []
    in_fence = False

    def flush() -> None:
        content = "\n".join(body).strip()
        if len(content) >= 30:
            sections.append(([name for _, name in stack], content))
        body.clear()

    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match:
            flush()
            level = len(match.group(1))
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, match.group(2)))
        else:
            body.append(line)
    flush()
    return sections


def chunk_markdown(
    title: str, text: str, max_chars: int = 800, overlap_chars: int = 150
) -> list[str]:
    chunks: list[str] = []
    for headings, body in split_sections(text):
        path = headings[1:] if headings and headings[0] == title else headings
        context = " > ".join([title, *path])
        for piece in chunk_text(body, max_chars, overlap_chars):
            chunks.append(f"{context}\n\n{piece}")
    return chunks
