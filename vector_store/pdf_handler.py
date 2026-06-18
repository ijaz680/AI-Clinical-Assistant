import os
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
import pdfplumber

# ─── ChromaDB Setup ────────────────────────────────────────────────────────────
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
os.makedirs(CHROMA_PATH, exist_ok=True)

_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        ef = embedding_functions.DefaultEmbeddingFunction()
        _collection = _client.get_or_create_collection(
            name="medical_docs",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def process_pdf(pdf_file) -> str:
    """Extract text from PDF, chunk it, and store embeddings."""
    try:
        collection = _get_collection()
        text = ""

        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return "⚠️ No readable text found in PDF."

        chunks = chunk_text(text)
        doc_name = pdf_file.name.replace(" ", "_")

        ids = [f"{doc_name}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": doc_name, "chunk": i} for i in range(len(chunks))]

        # Add to ChromaDB (upsert to avoid duplicates)
        collection.upsert(documents=chunks, ids=ids, metadatas=metadatas)

        # Track in session
        if "uploaded_pdfs" not in st.session_state:
            st.session_state["uploaded_pdfs"] = []
        if doc_name not in st.session_state["uploaded_pdfs"]:
            st.session_state["uploaded_pdfs"].append(doc_name)

        return f"✅ Processed '{pdf_file.name}' — {len(chunks)} chunks stored"

    except Exception as e:
        return f"❌ PDF Error: {str(e)}"


def search_context(query: str, n_results: int = 4) -> str:
    """Search vector store for relevant medical context."""
    try:
        collection = _get_collection()
        count = collection.count()
        if count == 0:
            return ""

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )
        if results and results["documents"]:
            docs = results["documents"][0]
            return "\n\n---\n".join(docs)
        return ""
    except Exception:
        return ""
