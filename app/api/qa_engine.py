from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
import copy
import faiss
from app.config import get_llm
from prometheus_client import Counter, Histogram, Summary
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from langchain.callbacks import StdOutCallbackHandler
from app.monitoring.otel_callback import OpenTelemetryCallback
import time
import os
from app.db.mongo import log_query, save_metadata
from app.ingest import parser, chunker, embedder, ner_graph
from datetime import datetime
from typing import Optional


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

def copy_original_vectorstore(vectorstore):
    new_faiss_index = faiss.clone_index(vectorstore.index)
    new_index_to_docstore_id = copy.deepcopy(vectorstore.index_to_docstore_id)
    new_docstore = copy.deepcopy(vectorstore.docstore)
    return FAISS(
        embedding_function=vectorstore.embedding_function,
        index=new_faiss_index,
        docstore=new_docstore,
        index_to_docstore_id=new_index_to_docstore_id
    )

async def ingest_file(file_path, username, session_id):
    for file in os.listdir(file_path):
        end_path = os.path.join(file_path, file)
        # Extract text
        text = parser.extract_text(end_path)
        chunks = chunker.chunk_text(text)
        # NER
        entities = ner_graph.extract_entities(text)

        # Store in MongoDB
        save_metadata(
            filename=file,
            chunks=chunks,
            entities=entities,
            username=username,
            session_id=session_id,
            upload_time=datetime.utcnow(),
        )

        new_vectorstore = copy_original_vectorstore(vectorstore)
        # Load new embeddings and merge
        await new_vectorstore.aadd_texts(chunks)
    return new_vectorstore  

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


async def get_answer(username: str, session_id: str, question: str, upload_dir: Optional[str] = None):
    start = time.perf_counter()
    qa_requests_total.inc()

    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("generate_answer") as span:
        span.set_attribute("username", username)
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

    if upload_dir is not None:
        curr_vectorstore = await ingest_file(upload_dir, username, session_id)
    else:
        curr_vectorstore = vectorstore

    # run RAG
    try:
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=curr_vectorstore.as_retriever(seach_kwargs={"k": 2}),
            memory=session_memory[session_id],
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": qa_prompt},
            callbacks=callbacks,#[StdOutCallbackHandler()]
        )

        result = await chain.ainvoke({"question": formatted_question})
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
        log_query(username, session_id, question, result, trace_id, latency)

        return {
            "answer": result["answer"],
            "trace_id": trace_id
        }
        # return result["answer"]
    except Exception as e:
        qa_failures.inc()
        raise e
