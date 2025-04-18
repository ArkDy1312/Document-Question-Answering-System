from app.ingest import chunker
import os

def test_chunking():
    text = "This is a test sentence. " * 100
    chunks = chunker.chunk_text(text, chunk_size=100, chunk_overlap=20)
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)
    assert len(chunks) > 1
