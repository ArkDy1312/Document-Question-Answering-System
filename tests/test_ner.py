from app.ingest import ner_graph

def test_entity_extraction_hf():
    text = "Barack Obama was born in Hawaii and served as President of the United States."
    entities = ner_graph.extract_entities(text)
    assert isinstance(entities, list)
    assert any("Obama" in e[0] or "Barack" in e[0] for e in entities)
