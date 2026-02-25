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

🎯Transform your semantic search into a complete **RAG(Retrieval-Augmented Generation)** sytem that:
* RETRIEVE relevant documents (you built this)
* AUGMENTS with context
* GENERATE perfect questions

* ✂️ Advanced Chunking for RAG
* 🔄 Evolution from Vector Databases Lab:
* Vector Databases Lab Strategy
    * Fixed 500 chars
    * 100 char overlap
→
RAG Strategy
Paragraph-based
Semantic boundaries
* 📊 Smart Chunking Visualization:
Document: [=========================================]
* ↓ Split by paragraphs
    * Paragraphs: [Para 1] [Para 2] [Para 3] [Para 4]
* ↓ Add 20% overlap
    * Chunks: [Chunk 1: Para1 + 20%Para2 ]
    * [Chunk 2: 80%Para2 + Para3 + 20%Para4]
    * [Chunk 3: 80%Para4 + Para5 ]
* Why paragraph-based? Preserves complete thoughts for better context in generation!