from app.db import mongo

def test_metadata_insertion():
    filename = "test_doc.pdf"
    chunks = ["Chunk 1", "Chunk 2"]
    entities = [("Obama", "PERSON")]
    mongo.save_metadata(filename, chunks, entities)

    # Optional: check document was inserted
    result = mongo.collection.find_one({"filename": filename})
    assert result is not None
    assert result["filename"] == filename