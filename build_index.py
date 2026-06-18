"""
Run this file ONCE to build the FAISS index from medical_data.txt
Command: python build_index.py
"""

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

def build_index():
    """Build the FAISS index from `medical_data.txt` and save to `data/embeddings`.
    Can be imported and called programmatically.
    """
    print("Building medical knowledge index...")
    os.makedirs("data/embeddings", exist_ok=True)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    with open("medical_data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    print(f"Found {len(chunks)} knowledge chunks...")

    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "data/embeddings/faiss_index.bin")
    with open("data/embeddings/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Index saved with {len(chunks)} medical knowledge chunks.")
    print("Now run: streamlit run app.py")


if __name__ == "__main__":
    build_index()
