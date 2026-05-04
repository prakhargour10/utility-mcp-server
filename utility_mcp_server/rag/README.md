# RAG Pipeline — A Beginner-to-Deep Walkthrough

> Audience: a working software engineer who has never built a RAG system before.
> Goal: explain **what** RAG is, **why** each stage exists, **what alternatives** you could have picked, and **why this codebase picked the choices it did**.

This document is the "design rationale" for the code in this folder:

```
utility_mcp_server/rag/
├── chunk.py      # Stage 1 — split docs/**/*.md into Chunk[] (sentence-aware)
├── embed.py      # Stage 2 — embed Chunks via local sentence-transformers -> float[384]
│                 #           + FAISS IndexFlatIP VectorStore (persisted to JSON)
├── store.py      # Process-wide singleton that lazy-loads the VectorStore
└── generate.py   # Stage 3 — retrieve top-k from FAISS (no LLM call)
```

The markdown corpus that feeds the pipeline lives in the repo at
``docs/`` (apis, models, languages, concepts) and is the single source of
truth for chunking + embedding. ``docs/get_documentation_list.json`` is
the master index served by the MCP tool layer.

---

## 1. What problem does RAG actually solve?

A plain LLM (e.g. Claude, GPT) is great at language but has three hard limits for a docs assistant:

1. **It doesn't know your private/recent docs.** Pine Labs SDK docs are not in its training set — at least not reliably and not at the version you care about.
2. **It hallucinates.** Asked about an API it doesn't truly know, it will *invent* function names, parameters, and error codes that look plausible.
3. **Re-training / fine-tuning is expensive** and is the wrong tool for "the docs changed yesterday."

**RAG = Retrieval-Augmented Generation.** Instead of teaching the model new facts, at query time you:

1. **Retrieve** the few most relevant snippets from your own corpus.
2. **Augment** the LLM prompt with those snippets as *context*.
3. **Generate** an answer that is *grounded* in (and cites) those snippets.

The LLM stops being "an oracle" and becomes "a reading-comprehension engine over your documents."

---

## 2. The 3-stage pipeline

```
                        ┌─────────────────────────────────────────────┐
                        │              OFFLINE / BUILD                │
                        ├─────────────────────────────────────────────┤
   docs/**/*.md   ──►  1. CHUNK   ──► Chunk[]                         │
                        │              │                               │
                        │              ▼                               │
                        │  2. EMBED   ──► EmbeddedChunk[]              │
                        │              │  (vector + text + metadata)   │
                        │              ▼                               │
                        │      data/embeddings.json (persisted store)  │
                        └─────────────────────────────────────────────┘
                                            │
                                            ▼
                        ┌─────────────────────────────────────────────┐
                        │               ONLINE / QUERY                │
                        ├─────────────────────────────────────────────┤
   user question ──► embed(question) ──► cosine search top-k          │
                                            │                         │
                                            ▼                         │
                                  build grounded prompt               │
                                            │                         │
                                            ▼                         │
                                3. GENERATE  (stitched chunks + cites) │
                                            │                         │
                                            ▼                         │
                                 answer + cited sources               │
                        └─────────────────────────────────────────────┘
```

Stages 1–2 are **build-time** (run once, persist). Stage 3 runs **per request**. Keeping that boundary clean is what makes a RAG system fast and cheap at query time.

---

## 3. Source corpus

**Job:** keep an authoritative copy of the source documents next to the code.

The documentation lives directly in the repository under `docs/` and is committed to source control. There is no build-time fetch from a remote docs site — chunking and embedding always read from the local files.

### Why a local in-repo corpus?
- **Determinism.** Build runs are reproducible; no remote site can change under us mid-run.
- **Decoupling.** Chunking/embedding don't care where bytes came from.
- **Diffability.** `git diff` on `docs/` shows exactly what changed.
- **Offline rebuilds.** Re-chunk/re-embed without any network.
- **Auditability.** Reviewers see the actual text being indexed in PRs.

---

## 4. Stage 1 — Chunking (`chunk.py`)

**Job:** split each markdown file into smaller, retrievable pieces (`Chunk` objects).

```python
@dataclass(frozen=True)
class Chunk:
    id: str            # "<route>#<index>", e.g. "api/init#0"
    text: str
    route: str         # "api/init"
    source_path: str
    index: int
    metadata: dict
```

### Why chunk at all?
Two hard reasons:

1. **Embedding models compress meaning into a fixed vector.** A whole 5-page doc squashed into one 1024-dim vector loses the per-section signal — every query looks "kind of similar" to it. Smaller chunks = sharper similarity.
2. **LLM context windows cost money and attention.** You only want to send the *relevant* paragraphs into the prompt, not the entire corpus.

### How we chunk
We use LlamaIndex's `SentenceSplitter` with `chunk_size=1024` tokens and `chunk_overlap=128` tokens.

- **Sentence-aware**, not byte-sliced — chunks don't cut mid-sentence.
- **Paragraph separator `"\n\n"`** respects markdown structure.
- **Overlap (~12%)** carries context across chunk boundaries so a sentence near the edge still has its surrounding meaning when retrieved.
- **Stable IDs** (`api/init#0`, `api/init#1`, …) are crucial — Stage 4 cites them in answers.

### Alternatives we did *not* pick (and why)
| Strategy | Trade-off |
|---|---|
| **Fixed-size character chunks** (e.g. every 1000 chars) | Simplest, but cuts mid-sentence and breaks semantic boundaries. Bad recall on Q&A. |
| **Whole-document chunks** | Vector becomes too "averaged"; retrieval is mushy; prompt is huge. |
| **One sentence per chunk** | Loses surrounding context; retrieval becomes noisy and citations explode. |
| **Markdown-structure-aware splitter** (split per `##` heading) | Better than fixed-size, but uneven — some sections are 50 tokens, others 5000. We get most of the benefit for free because `SentenceSplitter` already respects `\n\n`. |
| **Semantic / embedding-based chunking** (split where embedding similarity drops) | Higher quality but slower and more complex. Overkill for ~5 short docs. |
| **Code-aware AST chunking** | Right tool for *source code* corpora, not markdown docs. |

**Why this choice fits us:** the corpus is small (handful of `.md` files), structured with clear paragraphs, and we want **predictable, debuggable** chunks with citation IDs. `SentenceSplitter` + 1024/128 is the boring-but-correct default.

---

## 5. Stage 2 — Embeddings + Vector Store (`embed.py`)

This is the stage you flagged. There are actually **two** decisions here:

1. **Which embedding model?** → **`sentence-transformers/all-MiniLM-L6-v2`** (local, runs on CPU), output dim **384**, L2-normalized.
2. **Which vector store?** → A **FAISS `IndexFlatIP`** index over an in-memory `list[Chunk]`, persisted to `data/embeddings.json`.

### 5.1 What is an embedding, really?

An embedding model maps a piece of text to a fixed-length vector of floats (here, `float[1024]`) such that **texts with similar meaning land near each other in vector space**.

"Initialize the SDK" and "How do I call `init()`?" produce vectors with high cosine similarity even though they share almost no words. That's the whole magic — it lets us search by **meaning**, not by **keywords**.

### 5.2 Why `all-MiniLM-L6-v2` (local)?

| Criterion | MiniLM-L6-v2 | Why it matters here |
|---|---|---|
| **Quality** | Solid general-purpose English embeddings; widely benchmarked. | Our corpus is English technical docs. |
| **Dimensions** | 384 | Tiny on disk, fast to dot-product, plenty of signal for ~hundreds of chunks. |
| **Cost** | Zero per-query cost, zero network egress. | No vendor lock-in, no API key, no rate limits. |
| **Privacy** | Inference happens entirely in-process. | Docs and queries never leave the host. |
| **Footprint** | ~80 MB model download, CPU-friendly. | Fits on small PaaS hosts and laptops alike. |

### 5.3 Embedding alternatives we did *not* pick

| Option | Why not (for *this* project) |
|---|---|
| **OpenAI `text-embedding-3-small/large`** | Excellent, but adds a vendor + API key + per-call billing. We want a fully local pipeline. |
| **Bedrock Titan / Cohere Embed v3** (managed) | Strong, but require AWS credentials and network egress. Out of scope for the local mode. |
| **Larger sentence-transformers** (`bge-base-en`, `gte-large`, `e5-large`) | Higher quality, but several hundred MB and slower on CPU. MiniLM is the right size/speed trade-off for this corpus. |
| **Sparse / lexical (BM25, TF-IDF)** | Zero ML, instant. Great as a *complement*, but alone it can't match paraphrases ("init" vs "initialize"). Best used in a hybrid setup once you outgrow pure dense. |
| **Train your own embedding model** | Months of work, needs labeled pairs. Not justifiable for any project this size. |

### 5.4 Why an *in-memory* vector store with cosine similarity?

The store is literally:

```python
@dataclass
class VectorStore:
    items: list[EmbeddedChunk]   # text + metadata + float[1024]

    def search(self, query_vec, k):
        # cosine = dot product since vectors are normalized
        scored = [(dot(query_vec, x.embedding), x) for x in self.items]
        scored.sort(reverse=True)
        return scored[:k]
```

This is ~30 lines of code. It exists because of one number: **N**, the number of chunks.

| Corpus size | Right tool |
|---|---|
| **< 10k chunks** (us) | In-memory list + cosine. O(N) per query is microseconds. Zero infra. |
| 10k – 1M chunks | FAISS / hnswlib / Chroma / sqlite-vss locally. Approximate nearest neighbor (ANN) becomes worth the complexity. |
| 1M – 100M+ chunks | Managed vector DB (Pinecone, Weaviate, Qdrant Cloud, pgvector at scale, OpenSearch k-NN). Sharding, replication, hybrid search. |

**Our N is in the dozens.** Spinning up a vector DB would be pure ceremony — more moving parts to operate, more failure modes, more secrets to rotate, all to "speed up" a search that already takes <1 ms.

#### Why cosine similarity?
- The MiniLM embeddings are returned **L2-normalized** (we pass `normalize_embeddings=True`). For unit vectors, **cosine similarity == dot product**, which is exactly what FAISS `IndexFlatIP` computes.
- Cosine ignores vector magnitude and only compares **direction = meaning**, which is what we want for semantic similarity.
- Euclidean distance would also work on normalized vectors (it's monotonically related to cosine), so the choice is mostly idiomatic.

#### Why persist to `data/embeddings.json`?
- Embedding the full corpus runs the local model once per chunk → it costs **time** (and on cold start, a model download). We don't want to pay it on every server boot.
- JSON is human-readable, diffable, trivially portable, and good enough at this size. `store.py` lazy-loads it on first request and caches it for the process lifetime.

#### Alternatives we did *not* pick (yet)
| Option | When to switch |
|---|---|
| **FAISS / hnswlib** (in-process ANN) | When N grows past ~50k or query latency on a flat scan becomes noticeable. |
| **SQLite + `sqlite-vss`** | When you want SQL filtering alongside vector search and still no external service. |
| **`pgvector` on Postgres** | When you already run Postgres and want one DB for everything. |
| **Pinecone / Qdrant / Weaviate / Chroma server** | When you need multi-process, multi-host, hybrid search, metadata filtering at scale, or managed ops. |
| **Pickle / numpy `.npy` for the store** | Faster to load than JSON, but opaque. We chose readability over a few ms of load time. |

---

## 6. Stage 3 — Retrieve (`generate.py`)

**Job:** answer the user's question using the top-k retrieved chunks. There is **no LLM call** in local mode — the "answer" is a deterministic stitching of the retrieved chunk text plus their `[route#index]` citations, which the MCP client (or upstream LLM) can consume directly.

Pipeline per query:

1. **Embed the question** with the same local sentence-transformers model. (Critical: query and documents *must* use the same embedding space.)
2. **Search** the FAISS index for the top-k most similar chunks.
3. **Stitch** the chunks into a single answer block, each prefixed with its `[route#index]` id.
4. Return `GenerationResult { answer, sources[] }`.

### Why no LLM call in local mode?
The pipeline ships zero secrets and zero outbound calls. Citation-rich retrieval results are returned verbatim, so any caller (including a downstream LLM) can use them as grounded context without this server needing its own model credentials.

### Why such a strict system prompt?
The single biggest risk in RAG is the model **ignoring the context** and answering from its training data — which, for a private SDK, means **hallucinated APIs**. The system prompt is your last line of defense:

- "Answer ONLY using CONTEXT" → no leakage from training data.
- "If not in context, say exactly: *This is not documented…*" → forces an explicit refusal instead of a confident lie.
- "Quote identifiers verbatim" → no renamed `init()` → `initialize()` paraphrases.
- "Cite using [route#index]" → answers are auditable; users can click through.

### Retrieval knobs you can tune
| Knob | Effect |
|---|---|
| `top_k` | More chunks = more recall, larger prompt, more $$. |
| `chunk_size` / `overlap` (Stage 2) | Bigger chunks = more context per hit, fewer total hits. |
| `temperature` (Stage 4) | We use `0.2` — low, because we want faithful, deterministic answers, not creativity. |
| Re-ranker (not used) | A cross-encoder over top-20 → top-4 boosts precision when N is large. Not needed at our scale. |

---

## 7. Putting it together — end-to-end run

```bash
# Stage 1 (optional sanity check): inspect chunking
python -m utility_mcp_server.rag.chunk --json /tmp/chunks.json

# Stage 2: embed + persist the vector store
python -m utility_mcp_server.rag.embed --save data/embeddings.json

# Stage 3: ask a question
python -m utility_mcp_server.rag.generate \
    --load data/embeddings.json \
    --question "How do I initialize the Pine Labs SDK?"
```

In production (the MCP server), Stage 3 runs per request and `store.py` keeps the loaded `VectorStore` in memory for the whole process.

---

## 8. Summary of the choices and the *why*

| Stage | Choice | Why this, not that |
|---|---|---|
| Source | In-repo `docs/` markdown corpus, committed to git | Deterministic, diffable, decouples chunking from any network. |
| Chunk | LlamaIndex `SentenceSplitter`, 1024 tokens / 128 overlap, ID = `route#index` | Sentence-aware > byte-slicing; overlap preserves boundary context; stable IDs power citations. |
| Embed | Local **`all-MiniLM-L6-v2`**, 384-dim, normalized | Zero per-query cost, no network egress; strong quality; normalization makes cosine = dot product. |
| Vector store | **In-memory list + cosine**, persisted to `embeddings.json` | N is tiny → flat scan is microseconds. A vector DB would be ceremony, not value. JSON keeps it portable + auditable. Easy to swap later. |
| Retrieve | top-k = 4 over the in-memory store | Small, focused prompt → cheap, fast, and easy to cite. |
| Generate | None — deterministic stitching of retrieved chunks with `[route#index]` citations | Local mode ships no LLM credentials; the caller (or a downstream LLM) consumes the cited context directly. |

### The mental model to take with you

> **Build-time:** turn documents into *searchable meaning* (chunks → vectors → store).
> **Query-time:** turn a question into the *same kind of vector*, find the closest chunks, and let an LLM read them out loud — with citations and a leash.

Every "advanced" RAG technique you'll read about later (hybrid search, re-rankers, query rewriting, HyDE, multi-vector, graph RAG, agentic RAG) is an **upgrade to one of these stages**. Once the boring baseline works, you can swap one stage at a time and measure whether it actually helps your corpus and your users.
