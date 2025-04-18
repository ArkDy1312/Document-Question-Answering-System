from app.api.tools import summarize_text, entity_lookup
from app.api.agent import run_agent

def test_summarizer_tool():
    text = "This is a long passage about document question answering systems."
    summary = summarize_text(text)
    assert "summary" in summary.lower()

def test_entity_tool():
    entity = "Einstein"
    result = entity_lookup(entity)
    assert "Einstein" in result

def test_agent_run():
    result = run_agent("Summarize the following: The LangChain framework is used for RAG.")
    assert isinstance(result, str)
