This file captures **what was decided and why**, without restating architecture.

---

# Decisions – RAG Incident Assistant

This document records **architectural and design decisions** made while building the
RAG-based Spark / BFS incident assistant.

It exists to:
- explain *why* things are the way they are
- prevent reintroducing rejected designs
- serve as long-term context for future contributors

---

## Decision 1: Use LangGraph with Explicit Nodes

**Decision**  
Use LangGraph with explicit nodes and routers instead of a single chained RAG pipeline.

**Reasoning**
- Complex failure modes (hallucination vs missing data) require branching
- Deterministic retries need explicit control flow
- Debuggability requires visible state transitions

**Rejected**
- Linear RAG chains
- Implicit agent loops

---

## Decision 2: Separate Failure Modes Explicitly

**Decision**  
Treat hallucinations and missing knowledge as **different failure modes**.

**Definitions**
- Hallucination: model makes unsupported claims
- Missing knowledge: context is insufficient, model correctly refuses

**Reasoning**
- They require different fixes
- Mixing them causes unnecessary search, cost, and loops

**Result**
- Introduced `retry_generate` for hallucinations
- Introduced `improve_kb` for missing knowledge

---

## Decision 3: Retry Generation Before Improving KB

**Decision**  
Retry generation (once) before fetching new data.

**Reasoning**
- Hallucinations are often prompt/reasoning failures
- Retrying is cheaper than search
- Fetching more data does not fix bad reasoning

**Limits**
- `retry_generate` capped at **1**

---

## Decision 4: Cap Retries with Scoped Counters

**Decision**  
Use **scoped retry counters**, not a global retry counter.

**Counters**
- `retry_generation_count` ≤ 1
- `kb_retry_count` ≤ 3

**Reasoning**
- Different loops have different costs and purposes
- Global counters hide the reason for retries
- Scoped counters prevent infinite loops cleanly

---

## Decision 5: Introduce `kb_enriched` Signal

**Decision**  
Add a boolean signal indicating whether the knowledge base actually grew.

```python
kb_enriched = stored_chunks > 0
````

**Reasoning**

* Retrying search without new knowledge is wasteful
* Retrieved docs ≠ stored knowledge (duplicates, invalid sources)
* Router must know whether retries are productive

**Rejected**

* Using `bool(new_docs)` as enrichment signal

---

## Decision 6: Hybrid Relevance Grading

**Decision**
Use embedding similarity thresholds with LLM fallback only for borderline cases.

**Reasoning**

* Embeddings are fast, cheap, deterministic
* LLMs are expensive and non-deterministic
* Most relevance decisions do not require an LLM

**Relevance Rubric**

* Partial logs/configs → relevant
* Different system/job → irrelevant
* Borderline → LLM decides

---

## Decision 7: Zero-Tolerance Hallucination Policy

**Decision**
Any unsupported claim is a hallucination.

**Rules**

* Summarization allowed
* Rephrasing allowed
* Inference without evidence forbidden

**Reasoning**

* Incident analysis requires factual precision
* False positives are safer than false negatives

---

## Decision 8: Never Store LLM Output in Vector DB

**Decision**
Vector DB stores **only external source-of-truth documents**.

**Forbidden**

* Generated answers
* Summaries
* Reasoning traces
* Hypotheses

**Reasoning**

* Prevents self-reinforcing hallucinations
* Keeps KB factual and auditable
* Avoids long-term contamination

---

## Decision 9: Restrict Vector DB Writes to `improve_kb`

**Decision**
Only the `improve_kb` node may write to the vector DB.

**Reasoning**

* Centralizes KB growth
* Simplifies auditing and debugging
* Prevents accidental writes during generation

---

## Decision 10: Idempotent Vector DB Writes

**Decision**
All vector DB writes must be idempotent.

**Implementation**

* Content hashing
* Chunk-level IDs
* Deduplication before embedding

**Reasoning**

* Prevents duplicate storage
* Reduces embedding cost
* Enables safe retries

---

## Decision 11: Use Chroma for Early Development

**Decision**
Use Chroma as the vector DB during testing.

**Reasoning**

* Simple local persistence
* LangChain-native integration
* Easy migration to FAISS / managed DB later

**Constraint**

* Single embedding model per collection

---

## Decision 12: Persistent Vector DB Across Runs

**Decision**
Persist the vector DB to disk during development.

**Reasoning**

* Prevents re-indexing on restart
* Makes testing iterative and realistic
* Exposes KB growth behavior early

---

## Decision 13: Deterministic Termination Is Mandatory

**Decision**
All graph paths must terminate deterministically.

**Enforced By**

* Retry caps
* `kb_enriched` signal
* Explicit finalize state

**Reasoning**

* Prevents runaway costs
* Ensures predictable behavior in production

---

## Final Status

The system design now guarantees:

* Clear separation of concerns
* Bounded retries
* Safe KB growth
* No hallucination feedback loops
* Deterministic exits

This document should be updated **only when decisions change**, not for implementation details.

```

Just tell me which file you want next.
```
