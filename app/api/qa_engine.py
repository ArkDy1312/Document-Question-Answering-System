from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.config import get_llm
from prometheus_client import Counter, Histogram, Summary
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from langchain.callbacks import StdOutCallbackHandler
from app.monitoring.otel_callback import OpenTelemetryCallback
import time
from app.ingest.mongodb_utils import log_query


qa_requests_total = Counter("qa_requests_total", "Total number of QA requests")
qa_retrievals_per_query = Histogram("qa_retrievals_per_query", "Chunks retrieved per query")
qa_failures = Counter("qa_failures", "Failed QA generations")
qa_session_tokens = Histogram("qa_session_tokens", "Tokens in memory per session")
latency_per_qa = Histogram("latency_per_qa", "Latency per QA request")
callbacks = [OpenTelemetryCallback()]

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
    start = time.perf_counter()
    qa_requests_total.inc()

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("generate_answer") as span:
        span.set_attribute("session_id", session_id)
        span.set_attribute("question", question)

    # for current embedding model, we need to pass the "Query" also
    formatted_question = f"Query: {question}"

    if session_id not in session_memory:
        # memory = session_memory.setdefault(session_id, ConversationBufferMemory(
        #     memory_key="chat_history", return_messages=True,
        #     output_key="answer"
        # ))
        session_memory[session_id] = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True,
            output_key="answer"
        )

    # run RAG
    try:
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(seach_kwargs={"k": 2}),
            memory=session_memory[session_id],
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            callbacks=callbacks,#[StdOutCallbackHandler()]
        )

        result = chain.invoke({"question": formatted_question})
        result["chat_history"] = session_memory[session_id].chat_memory.messages

        end = time.perf_counter()
        latency = (end - start) * 1000  # ms

        qa_retrievals_per_query.observe(len(result["source_documents"]))
        # qa_session_tokens.observe(len(str(memory.load_memory_variables({}))))
        qa_session_tokens.observe(len(session_memory.keys()))
        latency_per_qa.observe(latency)

        # Get trace ID
        context = trace.get_current_span().get_span_context()
        trace_id = format(context.trace_id, "032x")

        # Log to Mongo
        log_query(session_id, question, result, trace_id, latency)

        return {
            "answer": result["answer"],
            "trace_id": trace_id
        }
        # return result["answer"]
    except Exception as e:
        qa_failures.inc()
        raise e
