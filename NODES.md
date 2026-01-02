This file defines **what each node must do and must never do**.

---
# Nodes – RAG Incident Assistant

This document defines **node-level contracts** for the LangGraph-based
RAG incident assistant.

Each node has:
- a single responsibility
- strict input/output expectations
- explicit forbidden behaviors

Nodes must not violate these contracts.

---

## Common Conventions

- Nodes operate on shared `GraphState`
- `documents` and `steps` are **append-only**
- Nodes must be **side-effect free** unless explicitly stated
- Only `improve_kb` may write to the vector DB

---

## GraphState (Relevant Fields)

```text
question
documents
generation

is_relevant
is_grounded

retry_generation_count
kb_retry_count
kb_enriched

steps
````

---

## 1. retrieve

### Responsibility

Fetch candidate documents from the vector DB.

### Inputs

* `question`

### Outputs

* `documents` (append-only)

### Side Effects

* Reads from vector DB

### Must

* Use semantic retrieval
* Return raw candidate docs
* Log step in `steps`

### Must NOT

* Filter documents
* Modify metadata
* Write to vector DB
* Generate answers

---

## 2. relevance_grader

### Responsibility

Filter retrieved documents to those relevant to the question.

### Strategy

* Embedding similarity thresholds
* LLM fallback only for borderline cases

### Inputs

* `question`
* `documents`

### Outputs

* filtered `documents`
* `is_relevant` (`"yes"` or `"no"`)

### Side Effects

* None

### Must

* Be liberal but firm
* Accept partial logs/configs
* Reject unrelated systems/jobs
* Log step in `steps`

### Must NOT

* Fetch new documents
* Write to vector DB
* Generate answers

---

## 3. generate

### Responsibility

Produce a grounded answer using filtered documents.

### Inputs

* `question`
* `documents`

### Outputs

* `generation`

### Side Effects

* None

### Must

* Use only provided documents
* Refuse when context is insufficient:

  ```text
  I don't know - The current knowledge base is insufficient to answer this.
  ```
* Log step in `steps`

### Must NOT

* Infer missing facts
* Hallucinate configs or causes
* Write to vector DB

---

## 4. hallucination_grader

### Responsibility

Detect unsupported claims in the generated answer.

### Inputs

* `documents`
* `generation`

### Outputs

* `is_grounded` (`"yes"` or `"no"`)

### Side Effects

* None

### Must

* Use structured output
* Reject any unsupported claim
* Treat refusals as grounded
* Log step in `steps`

### Must NOT

* Generate answers
* Fetch documents
* Modify documents

---

## 5. retry_generate

### Responsibility

Regenerate the answer after hallucination detection.

### Trigger Condition

* `is_grounded == "no"`

### Inputs

* `question`
* `documents`

### Outputs

* `generation`
* increment `retry_generation_count`

### Side Effects

* None

### Must

* Use stricter prompt
* Remove unsupported claims
* Log step in `steps`

### Must NOT

* Fetch new documents
* Write to vector DB
* Retry more than once

---

## 6. improve_kb

### Responsibility

Enrich the knowledge base with new external documents.

### Trigger Condition

* Answer is grounded
* Answer is `"I don't know"`

### Inputs

* `question`
* `kb_retry_count`

### Outputs

* `documents` (new docs only)
* `kb_retry_count` (incremented)
* `kb_enriched` (boolean)

### Side Effects

* Writes to vector DB

### Must

* Rewrite query for better recall
* Fetch external source-of-truth docs
* Validate sources
* Normalize content
* Chunk documents
* Deduplicate before embedding
* Upsert idempotently
* Set:

  ```python
  kb_enriched = stored_chunks > 0
  ```
* Log step in `steps`

### Must NOT

* Generate answers
* Modify existing documents
* Store LLM-generated text

---

## Node Interaction Rules

* `retrieve` → `relevance_grader`
* `relevance_grader` → `generate` OR `improve_kb`
* `generate` → `hallucination_grader`
* `hallucination_grader` → `retry_generate` OR `improve_kb` OR finalize
* `improve_kb` → `retrieve`

No other transitions are allowed.

---

## Invariants

* Vector DB contains **only external documents**
* Generated text is **never persisted**
* All loops are bounded
* State transitions are deterministic

---

## Enforcement

Violating these contracts is a bug.
Changes require updates to:

* `ARCHITECTURE.md`
* `DECISIONS.md`



Just say which one you want next.
```
