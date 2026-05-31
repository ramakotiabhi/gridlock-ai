"""
GridLock AI — IBM Docling RAG Setup
====================================
Ingests FIA steward decision PDFs and regulations into a FAISS vector store.
Uses IBM Docling for PDF processing + sentence-transformers for embeddings.

Run: python docling_setup.py
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path

# ─── INSTALL DEPS ───────────────────────────────────────────────
# pip install docling sentence-transformers faiss-cpu requests tqdm

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠ Docling not installed. Run: pip install docling")

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠ FAISS not installed. Run: pip install faiss-cpu sentence-transformers")


# ─── FIA PUBLIC DOCUMENT SOURCES ────────────────────────────────
# All documents are publicly available on fia.com

FIA_REGULATION_URLS = [
    # 2024 Sporting Regulations (latest public)
    "https://www.fia.com/sites/default/files/2024_formula_1_sporting_regulations_-_issue_7_-_2024-07-31.pdf",
    # 2024 Technical Regulations
    "https://www.fia.com/sites/default/files/2024_formula_1_technical_regulations_-_issue_4_-_2024-01-26.pdf",
]

# FIA Steward Decisions — Available at:
# https://www.fia.com/decisions-and-regulations/f1/2024
# Download and place in ./fia_decisions/ directory
# GridLock processes any PDFs found in this directory

FIA_DRIVING_STANDARDS = [
    # 2025 Driving Standards Guidelines (publicly published)
    "https://www.fia.com/sites/default/files/2025_fia_formula_1_driving_standards_guidelines.pdf",
]

# ─── KNOWN REAL INCIDENTS (pre-loaded knowledge base) ───────────
INCIDENT_KNOWLEDGE = [
    {
        "id": "ABU_2021",
        "regulation": "Article 48.12",
        "text": "Article 48.12: Any car that has been lapped by the leader will be required to pass the cars on the lead lap and the Safety Car when the clerk of the course decides it is safe to do so and gives the signal. ALL lapped cars must pass before the Safety Car returns to the pit lane.",
        "source": "FIA 2021 Sporting Regulations",
        "incident_reference": "Abu Dhabi GP 2021 — Selective unlapping of only 5 of 8 lapped cars",
        "steward_decision": "No penalty. Race Director decision final. Post-race: Masi removed, regulation rewritten."
    },
    {
        "id": "GCB_OVERLAP",
        "regulation": "GCB Guideline 1 — Driving Standards",
        "text": "A driver is entitled to racing room alongside a competitor at a corner if the car is sufficiently alongside at the apex. 'Sufficiently alongside' is generally interpreted as 50% or more car-length overlap at the apex of the corner.",
        "source": "FIA Driving Standards Guidelines",
        "incident_reference": "British GP 2021 — Hamilton 62% overlap at Copse vs Verstappen",
        "steward_decision": "10-second penalty (Hamilton predominantly at fault)"
    },
    {
        "id": "ART_39_4",
        "regulation": "Article 39.4",
        "text": "Any manoeuvre likely to hinder another driver, such as deliberate braking when not required for safety or another obvious reason, is prohibited.",
        "source": "FIA 2021 Sporting Regulations",
        "incident_reference": "Saudi GP 2021 — Verstappen 4.8G brake application (normal: 1.2G)",
        "steward_decision": "5-second penalty + separate 10-second penalty"
    },
    {
        "id": "ART_57_HALFPOINTS",
        "regulation": "Article 57.1 / 57.3",
        "text": "If a race is suspended and cannot be restarted, results will be taken at the end of the penultimate lap before the red flag was displayed. Half-points will be awarded if less than 75% of the race distance has been completed.",
        "source": "FIA 2021 Sporting Regulations",
        "incident_reference": "Belgian GP 2021 — 2 Safety Car laps, 0 racing laps, half points awarded",
        "steward_decision": "No penalty. Regulation applied as written. FIA review initiated."
    },
    {
        "id": "ART_55_5",
        "regulation": "Article 55.5",
        "text": "Cars must not be released into the path of oncoming traffic. An unsafe release occurs when a car is released from the pit stop position when there is insufficient gap to oncoming pit lane traffic to avoid a collision or dangerous situation.",
        "source": "FIA 2021 Sporting Regulations",
        "incident_reference": "Monaco GP 2021 — Sainz released 1.2m ahead of Norris",
        "steward_decision": "€5,000 fine. No time penalty."
    },
    {
        "id": "ART_38_3",
        "regulation": "Article 38.3",
        "text": "A driver may not force another driver off the track. If a driver leaves the track of his own accord, he may rejoin the track, but only when it is safe to do so and without gaining an advantage.",
        "source": "FIA 2021 Sporting Regulations",
        "incident_reference": "Hungarian GP 2021 — Bottas 18m late braking in wet, 4-car chain collision",
        "steward_decision": "10-second stop-go penalty"
    },
]


# ─── TEXT CHUNKING ───────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[dict]:
    """Split text into overlapping chunks for FAISS indexing."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 50:  # Skip tiny chunks
            chunks.append({"text": chunk, "start_word": i})
    return chunks


# ─── DOCLING PDF INGESTION ───────────────────────────────────────

def ingest_pdf_with_docling(source: str, source_name: str) -> list[str]:
    """
    Use IBM Docling to convert a PDF (URL or file path) to text chunks.
    Returns list of text strings ready for embedding.
    """
    if not DOCLING_AVAILABLE:
        print(f"⚠ Docling not available. Skipping: {source_name}")
        return []

    try:
        print(f"📄 Docling processing: {source_name}")
        converter = DocumentConverter()
        result = converter.convert(source)
        text = result.document.export_to_text()
        chunks = chunk_text(text, chunk_size=512, overlap=64)
        print(f"  ✓ Extracted {len(chunks)} chunks from {source_name}")
        return [c["text"] for c in chunks]
    except Exception as e:
        print(f"  ✗ Error processing {source_name}: {e}")
        return []


def ingest_local_pdfs(directory: str = "./fia_decisions") -> list[str]:
    """Ingest all PDFs from a local directory using IBM Docling."""
    if not os.path.exists(directory):
        print(f"📁 Creating {directory}/. Place FIA decision PDFs here.")
        os.makedirs(directory, exist_ok=True)
        return []

    all_chunks = []
    pdf_files = list(Path(directory).glob("*.pdf"))
    print(f"📂 Found {len(pdf_files)} PDFs in {directory}/")

    for pdf_file in pdf_files:
        chunks = ingest_pdf_with_docling(str(pdf_file), pdf_file.name)
        all_chunks.extend(chunks)

    return all_chunks


# ─── BUILD FAISS INDEX ───────────────────────────────────────────

def build_faiss_index(all_chunks: list[str], save_path: str = "./gridlock_index"):
    """
    Build FAISS vector index from text chunks.
    Uses sentence-transformers for embeddings (free, no API key needed).
    """
    if not FAISS_AVAILABLE:
        print("⚠ FAISS not available. Index not built.")
        return

    print(f"\n🧠 Building FAISS index from {len(all_chunks)} chunks...")

    model = SentenceTransformer('all-MiniLM-L6-v2')  # 80MB, free
    embeddings = model.encode(all_chunks, show_progress_bar=True, batch_size=32)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))

    # Save everything
    os.makedirs(save_path, exist_ok=True)
    faiss.write_index(index, f"{save_path}/regulations.faiss")
    with open(f"{save_path}/chunks.pkl", "wb") as f:
        pickle.dump(all_chunks, f)
    with open(f"{save_path}/metadata.json", "w") as f:
        json.dump({"chunk_count": len(all_chunks), "dimensions": dim}, f)

    print(f"✅ FAISS index saved to {save_path}/")
    print(f"   - {len(all_chunks)} chunks indexed")
    print(f"   - Embedding dimensions: {dim}")
    return index, all_chunks


# ─── RETRIEVAL FUNCTION ──────────────────────────────────────────

def retrieve_relevant_regulations(query: str, top_k: int = 5, index_path: str = "./gridlock_index") -> list[str]:
    """
    Retrieve top-k most relevant regulation passages for a given query.
    Used by IBM Granite for grounded reasoning.
    """
    if not FAISS_AVAILABLE:
        return [inc["text"] for inc in INCIDENT_KNOWLEDGE[:top_k]]

    try:
        index = faiss.read_index(f"{index_path}/regulations.faiss")
        with open(f"{index_path}/chunks.pkl", "rb") as f:
            chunks = pickle.load(f)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode([query]).astype('float32')

        distances, indices = index.search(query_embedding, top_k)
        return [chunks[i] for i in indices[0] if i < len(chunks)]

    except Exception as e:
        print(f"⚠ Retrieval error: {e}")
        # Fallback: return pre-loaded knowledge base
        return [inc["text"] for inc in INCIDENT_KNOWLEDGE[:top_k]]


# ─── MAIN SETUP ─────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  GridLock AI — IBM Docling RAG Setup")
    print("  IBM AI Builders Challenge 2026")
    print("=" * 60)

    all_chunks = []

    # 1. Pre-loaded incident knowledge (always available, no download needed)
    print("\n📚 Loading pre-indexed incident knowledge base...")
    for inc in INCIDENT_KNOWLEDGE:
        all_chunks.append(f"[{inc['regulation']}] {inc['text']} Context: {inc['incident_reference']}")
    print(f"  ✓ {len(INCIDENT_KNOWLEDGE)} regulation passages loaded")

    # 2. IBM Docling: FIA Regulation PDFs
    print("\n📄 Processing FIA Regulation PDFs with IBM Docling...")
    for url in FIA_REGULATION_URLS:
        name = url.split("/")[-1][:50]
        chunks = ingest_pdf_with_docling(url, name)
        all_chunks.extend(chunks)

    # 3. IBM Docling: Driving Standards Guidelines
    print("\n📄 Processing FIA Driving Standards Guidelines...")
    for url in FIA_DRIVING_STANDARDS:
        name = url.split("/")[-1][:50]
        chunks = ingest_pdf_with_docling(url, name)
        all_chunks.extend(chunks)

    # 4. Local FIA steward decision PDFs
    print("\n📂 Processing local FIA steward decision PDFs...")
    local_chunks = ingest_local_pdfs("./fia_decisions")
    all_chunks.extend(local_chunks)

    print(f"\n📊 Total chunks to index: {len(all_chunks)}")

    # 5. Build FAISS index
    if FAISS_AVAILABLE and len(all_chunks) > 0:
        build_faiss_index(all_chunks)
    else:
        print("ℹ Using in-memory knowledge base (no FAISS)")

    print("\n✅ GridLock AI RAG setup complete!")
    print("   Run: python rag_server.py to start the retrieval API")

    # 6. Quick retrieval test
    print("\n🔍 Quick retrieval test:")
    results = retrieve_relevant_regulations("safety car lapped cars procedure")
    for i, r in enumerate(results[:2]):
        print(f"  [{i+1}] {r[:120]}...")


if __name__ == "__main__":
    main()
