# GridLock AI — System Architecture

## Pipeline Flow

```
OpenF1 API (Real Telemetry)
        ↓
Feature Extraction Layer
        ↓
IBM Docling RAG ←── FIA PDFs (500+ docs, 2010-2026)
        ↓
IBM Granite 3.1-8B-Instruct
        ↓
Output Router
   ├── Steward Brief (60-second structured decision support)
   ├── Fan Explainer (plain language for 500M+ fans)
   └── Team Appeal Brief (0-100 appeal strength score)
```

## IBM Tools Integration

### IBM Granite
- Model: `ibm-granite/granite-3.1-8b-instruct`
- Via: HuggingFace free serverless inference
- Temperature: 0.2 (deterministic legal reasoning)
- Used for: Steward brief, appeal scoring, fan explainer, penalty simulator

### IBM Docling
- Ingests 500+ FIA steward decision PDFs (2010-2026)
- Chunks: 512 tokens with 64 overlap
- Embeddings: sentence-transformers all-MiniLM-L6-v2
- Vector store: FAISS IndexFlatL2

### Langflow
- Visual pipeline orchestration
- Config: pipeline/gridlock_langflow.json
- Connects all components visually for demo

## Data Sources
- OpenF1 API: api.openf1.org (free, no auth)
- FastF1: Historical race data 2018-2026
- FIA steward decisions: fia.com/decisions-and-regulations (public)
- FIA regulations: fia.com (public domain)
