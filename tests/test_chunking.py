from app.chunking import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("Hello world. This is short.") == ["Hello world. This is short."]


def test_empty_text_gives_no_chunks():
    assert chunk_text("   \n\n  ") == []


def test_long_text_splits_and_respects_limit():
    text = " ".join(f"Sentence number {i} is here." for i in range(100))
    chunks = chunk_text(text, max_chars=200, overlap_chars=50)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_chunks_overlap():
    text = " ".join(f"Sentence number {i} is here." for i in range(100))
    chunks = chunk_text(text, max_chars=200, overlap_chars=50)
    last_sentence_of_first = chunks[0].split(". ")[-1]
    assert last_sentence_of_first in chunks[1]
