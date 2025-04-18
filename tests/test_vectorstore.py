from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def main():
    print("Loading vectorstore...")
    vectorstore = FAISS.load_local(
        "data/faiss",
        HuggingFaceEmbeddings(model_name="thenlper/gte-small"),
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    print("Vectorstore ready. Type 'exit' to quit.")
    while True:
        query = input("\nQuery: ")
        if query.strip().lower() in ["exit", "quit"]:
            break

        results = retriever.invoke(query)
        if not results:
            print("No documents found.")
            continue

        for i, doc in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(doc.page_content)
            print(f"Metadata: {doc.metadata}")

if __name__ == "__main__":
    main()
