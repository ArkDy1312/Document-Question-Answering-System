import fitz  # PyMuPDF

# Extract text from PDF using PyMuPDF
def parse_pdf(filepath: str) -> str:
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        page_text = page.get_text()
        text += page_text + "\n"
    return text.strip()

# Extract text from TXT files
def parse_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# Dispatcher based on file extension
def extract_text(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        return parse_pdf(filepath)
    elif filepath.endswith(".txt"):
        return parse_txt(filepath)
    else:
        raise ValueError("Unsupported file format: " + filepath)