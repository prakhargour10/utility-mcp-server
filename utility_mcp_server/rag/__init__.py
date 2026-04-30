"""RAG (Retrieval-Augmented Generation) pipeline for Pine Labs docs.

Pipeline stages:

    Raw Docs (markdown fetched from docs site)
        -> Chunking (LlamaIndex SentenceSplitter)
            -> Embedding (Bedrock Titan)
                -> In-memory vector store
                    -> Query / similarity search
                        -> LLM (Bedrock Claude) answer

This package currently implements stage 1 (ingestion). Subsequent stages
will be added incrementally.
"""
