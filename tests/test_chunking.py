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
from app.chunking import chunk_markdown


def test_chunks_carry_heading_path():
    text = (
        "## Setup\n\nInstall the tool first and then configure it carefully.\n\n"
        "### Advanced\n\nSet the flag to enable advanced mode for experts."
    )
    chunks = chunk_markdown("Guide", text)
    assert chunks[0].startswith("Guide > Setup\n\n")
    assert chunks[1].startswith("Guide > Setup > Advanced\n\n")


def test_hash_inside_code_fence_is_not_a_heading():
    text = "## Run\n\n```\n# this is a comment\necho hi\n```\n\nThen check the output of the command."
    chunks = chunk_markdown("Guide", text)
    assert len(chunks) == 1
    assert "# this is a comment" in chunks[0]
