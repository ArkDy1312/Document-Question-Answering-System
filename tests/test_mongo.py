from app.ingest import mongodb_utils

def test_metadata_insertion():
    filename = "test_doc.pdf"
    chunks = ["Chunk 1", "Chunk 2"]
    entities = [("Obama", "PERSON")]
    mongodb_utils.save_metadata(filename, chunks, entities)

    # Optional: check document was inserted
    result = mongodb_utils.collection.find_one({"filename": filename})
    assert result is not None
    assert result["filename"] == filename