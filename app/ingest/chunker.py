from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

def clean_and_split_paragraphs(text: str):
    # Remove citations, table lines, etc.
    text = re.sub(r'\[\d+\]', '', text)  # Remove citations like [12]
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize paragraph breaks
    paragraphs = text.strip().split("\n\n")
    return [p.strip() for p in paragraphs if len(p.strip()) > 100]  # filter short ones

def chunk_text(text: str, chunk_size=500, chunk_overlap=200):
    paragraphs = clean_and_split_paragraphs(text)

    # Join paragraphs to create a cleaned base text
    cleaned_text = "\n\n".join(paragraphs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
    )
    return splitter.split_text(cleaned_text)
