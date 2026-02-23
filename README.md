# AI

* LLM models to explore:
    * google/gemini-2.5-flash
    * x-ai/grok-code-fast-1

* Prompt engineering
    * Zero-shot prompting - Direct commands without examples
    * One-shot prompting - Learning from a single example
    * Few-shot prompting - Multiple examples for consistency
    * Chain-of-thought - Step-by-step reasoning

* Vector DB: store embeddings

🎯 What are Vector Stores?
* Vector stores are specialized databases designed to:

    * Store embeddings (vectors) efficiently
    * Find similar vectors lightning-fast
    * Scale to millions of documents
    * Attach metadata for filtering
🔄 How Vector Search Works
1. Document → Embedding → Store in DB
2. Query → Embedding → Find Similar
3. Return Top K Results (by cosine similarity)

Example:
Query: "remote work policy" [0.2, 0.8, ...]
  ↓
Finds: "work from home guidelines" [0.21, 0.79, ...]
       (98% similar!)
⚡ Why ChromaDB?
Local-first: No cloud dependency
Production-ready: Used by real companies
Simple API: 5 lines to get started
Metadata filtering: Search by tags, dates, categories