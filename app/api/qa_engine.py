from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.config import get_llm
from prometheus_client import Counter, Histogram
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from app.monitoring.otel_callback import OpenTelemetryCallback
import time
from app.ingest.mongodb_utils import log_query


# qa_requests_total = Counter("qa_requests_total", "Total number of QA requests")
# qa_retrievals_per_query = Histogram("qa_retrievals_per_query", "Chunks retrieved per query")
# qa_failures = Counter("qa_failures", "Failed QA generations")
# qa_session_tokens = Histogram("qa_session_tokens", "Tokens in memory per session")
# callbacks = [OpenTelemetryCallback()]

# Load FAISS with BGE embeddings
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en",
    encode_kwargs={"normalize_embeddings": True}
)
vectorstore = FAISS.load_local(
    "data/faiss",
    embedding_model,
    allow_dangerous_deserialization=True
)

# Load QA model wrapped with ChatHuggingFace
llm = get_llm(type="qa")

# In-memory session memory store
session_memory = {}

# Prompt template for document QA
qa_prompt = PromptTemplate.from_template("""
Answer the question using the context below.

                                                              
Context:
{context}

Question: {question}
Answer:
""")


def get_answer(session_id: str, question: str):
    # for current embedding model, we need to pass the "Query" also
    formatted_question = f"Query: {question}"

    if session_id not in session_memory:
        session_memory[session_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True,
            output_key="answer"
        )

    # run RAG
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(seach_kwargs={"k": 2}),
        memory=session_memory[session_id],
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": qa_prompt}
    )
    

    result = chain.invoke({"question": formatted_question})
    return result["answer"]
