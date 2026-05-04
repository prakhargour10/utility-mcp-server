"""RAG (Retrieval-Augmented Generation) pipeline for Pine Labs docs.

Pipeline stages:

    Local docs (markdown corpus under ``docs/``)
        -> Chunking (LlamaIndex SentenceSplitter)
            -> Embedding (Bedrock Titan v2)
                -> FAISS in-memory dense vector store
                    -> Query / similarity search
"""
