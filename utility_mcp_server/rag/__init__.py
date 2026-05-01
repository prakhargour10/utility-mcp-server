"""RAG (Retrieval-Augmented Generation) pipeline for Pine Labs docs.

Pipeline stages:

    Local docs (markdown corpus under ``docs/``)
        -> Chunking (LlamaIndex SentenceSplitter)
            -> Embedding (Bedrock Titan)
                -> In-memory vector store
                    -> Query / similarity search
                        -> LLM (Bedrock Claude) answer
"""
