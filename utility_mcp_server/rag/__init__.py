"""RAG (Retrieval-Augmented Generation) pipeline for Pine Labs docs.

Pipeline stages:

    Local docs (markdown corpus under ``docs/``)
        -> Chunking (LlamaIndex SentenceSplitter)
            -> Embedding (local sentence-transformers, default `all-MiniLM-L6-v2`)
                -> FAISS in-memory dense vector store
                    -> Query / similarity search
"""
