from app.ingest import embedder
from pathlib import Path
import shutil

def test_faiss_save_and_exists(tmp_path):
    chunks = ["This is a test chunk.", "Another test chunk for embeddings."]
    save_path = tmp_path / "faiss_data"

    embedder.save_to_faiss(chunks, str(save_path))

    index_file = save_path / "index.faiss"
    pkl_file = save_path / "index.pkl"

    assert index_file.exists()
    assert pkl_file.exists()

    # ✅ Cleanup (optional, for safety)
    if save_path.exists():
        shutil.rmtree(save_path)