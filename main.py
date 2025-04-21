from app.db import mongo
from app.ingest import parser, chunker, embedder, ner_graph

# Example usage
path = "data/uploads/sample.pdf"

existing = mongo.collection.find_one({"filename": path})

if existing:
    print(f"Skipping '{path}' — already exists in DB.")
else:
    text = parser.extract_text(path)
    # Make chunks
    chunks = chunker.chunk_text(text)
    # Save to FAISS using LangChain embeddings
    embedder.save_to_faiss(chunks)
    # USE HF NER
    entities = ner_graph.extract_entities(text) # HF or spaCy
    # Store in MongoDB
    mongo.save_metadata(path, chunks, entities)
