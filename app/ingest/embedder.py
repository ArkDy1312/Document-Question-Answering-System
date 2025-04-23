# Using Huging Face for Embedding
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Hugging Face embedding model (e.g., BGE, MiniLM, etc.)
MODEL_NAME = "BAAI/bge-base-en"

# Create LangChain-compatible embedder
embedder = HuggingFaceEmbeddings(model_name=MODEL_NAME)

# Optionally, you can use SentenceTransformer for embedding
# from sentence_transformers import SentenceTransformer
# model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# def embed_chunks(chunks):
#     return model.encode(chunks, show_progress_bar=True)

def save_to_faiss(chunks, faiss_dir="data/faiss"):
    """
    Save chunks to FAISS vector store.
    Args:
        chunks (list): List of text chunks.
        faiss_dir (str): Directory to save the FAISS index.
    """
    # Create FAISS vector store
    vectorstore = FAISS.from_texts(chunks, embedding=embedder) 
    vectorstore.save_local(faiss_dir)