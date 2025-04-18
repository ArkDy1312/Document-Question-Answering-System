from app.ingest import parser, chunker, embedder, mongodb_utils, ner_graph

# Example usage
path = "data/uploads/sample.pdf"
text = parser.extract_text(path)

# Make chunks
chunks = chunker.chunk_text(text)

# Save to FAISS using LangChain embeddings
embedder.save_to_faiss(chunks)

# USE HF NER
entities = ner_graph.extract_entities(text) # HF or spaCy

# Store in MongoDB
mongodb_utils.save_metadata(path, chunks, entities)
