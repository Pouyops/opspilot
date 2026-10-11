import re
import sys
from pathlib import Path

import httpx

API = "http://localhost:8000/documents"
DONE_FILE = Path(".ingested.txt")

FRONT = re.compile(r"\A(---|\+\+\+)\s*\n(.*?)\n\1\s*\n", re.S)
TITLE = re.compile(r"""^title\s*[:=]\s*["']?(.+?)["']?\s*$""", re.M)
SHORTCODE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")


def clean(raw: str, path: Path) -> tuple[str, str]:
    title = path.stem.replace("-", " ").title()
    match = FRONT.match(raw)
    if match:
        found = TITLE.search(match.group(2))
        if found:
            title = found.group(1)
        raw = raw[match.end():]
    raw = HTML_COMMENT.sub("", raw)
    raw = SHORTCODE.sub("", raw)
    raw = IMAGE.sub("", raw)
    raw = LINK.sub(r"\1", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw).strip()
    return title[:200], raw


def main(root: str, limit: int = 40, min_chars: int = 800) -> None:
    done = set(DONE_FILE.read_text().splitlines()) if DONE_FILE.exists() else set()
    base = Path(root)
    sent = 0
    for path in sorted(base.rglob("*.md")):
        source = str(path.relative_to(base))
        if source in done:
            continue
        title, text = clean(path.read_text(encoding="utf-8", errors="ignore"), path)
        if len(text) < min_chars:
            continue
        r = httpx.post(
            API,
            json={"title": title, "source": source[:500], "text": text},
            timeout=600,
        )
        print(r.status_code, source, r.json().get("chunk_count"))
        if r.status_code == 201:
            with DONE_FILE.open("a") as f:
                f.write(source + "\n")
            sent += 1
        if sent >= limit:
            break


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40)
