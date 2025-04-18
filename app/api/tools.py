from langchain.tools import Tool
from app.config import get_llm

summarizer_llm = get_llm(type="summarizer")

def summarizer_fn(text: str) -> str:
    return summarizer_llm.invoke(f"Summarize this:\n\n{text}")

summarizer_tool = Tool(
    name="Summarizer",
    func=summarizer_fn,
    description="Use this to summarize any given text or paragraph."
)

ner_llm = get_llm(type="ner")

def entity_extractor(text: str) -> str:
    prompt = f"Extract named entities from this text:\n\n{text}"
    return ner_llm.invoke(prompt)

entity_tool = Tool(
    name="EntityExtractor",
    func=entity_extractor,
    description="Extracts people, places, organizations, and other entities from text."
)