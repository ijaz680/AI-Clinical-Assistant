from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

_model = None
_index = None
_chunks = None

def _load():
    global _model, _index, _chunks
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    if _index is None:
        index_path = "data/embeddings/faiss_index.bin"
        chunks_path = "data/embeddings/chunks.json"
        if not os.path.exists(index_path):
            # Attempt to build the index automatically if possible
            try:
                import build_index

                print("FAISS index not found — building now by running build_index.build_index()")
                build_index.build_index()
            except Exception:
                raise FileNotFoundError(
                    "FAISS index not found and automatic build failed. Please run: python build_index.py"
                )
        _index = faiss.read_index(index_path)
        with open(chunks_path, encoding="utf-8") as f:
            _chunks = json.load(f)

def search(query, top_k=3):
    _load()
    vec = _model.encode([query]).astype("float32")
    _, indices = _index.search(vec, top_k)
    results = [_chunks[i] for i in indices[0] if i < len(_chunks)]
    return results
