# Optionally use spacy
# import spacy

# nlp = spacy.load("en_core_web_sm")

# # Function to extract named entities from text
# def extract_entities(text: str):
#     doc = nlp(text)
#     return list(set((ent.text, ent.label_) for ent in doc.ents))

# Using Hugging Face Transformers for NER
from transformers import pipeline

ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# Function to extract named entities from text
def extract_entities(text):
    results = ner_pipeline(text)
    return list(set((ent["word"], ent["entity_group"]) for ent in results))
