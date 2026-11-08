# 004 — RAG Retrieval Investigation

## Status

**Validated**

## Date

2026

## System Context

* Project: `LocalAIAgentWithRAG`
* Architecture: local-first Retrieval-Augmented Generation
* Language: Python
* Vector database: ChromaDB
* Framework: LangChain
* Local model runtime: Ollama
* Dataset: restaurant reviews

---

## 1. Objective

The objective was to establish that the RAG pipeline was not merely launching successfully, but actually performing retrieval and using retrieved information to produce answers.

The investigation focused on the complete data flow:

```text
Source documents
      ↓
Loading
      ↓
Chunking
      ↓
Embeddings
      ↓
Vector storage
      ↓
Similarity retrieval
      ↓
Retrieved context
      ↓
LLM
      ↓
Generated answer
```

---

## 2. Why Startup Was Not Enough

A RAG application can start successfully while retrieval is completely broken.

Therefore:

```text
Application starts
        ≠
RAG works
```

Likewise:

```text
Vector database exists
        ≠
Relevant documents are retrieved
```

and:

```text
LLM produces an answer
        ≠
Answer was grounded in retrieved context
```

The system therefore required behavioral validation.

---

## 3. Data Source

The project used:

```text
data/realistic_restaurant_reviews.csv
```

The dataset provided realistic restaurant-review content suitable for testing semantic retrieval.

---

## 4. Ingestion Pipeline

The intended ingestion flow was:

```text
CSV
 ↓
CSV loader
 ↓
Document objects
 ↓
Chunking
 ↓
Embedding generation
 ↓
Chroma persistence
```

Relevant project components included:

```text
ingestion/
├── chunker.py
└── loaders/
    └── csv_loader.py
```

---

## 5. Vector Storage

The project used a persistent Chroma vector store.

The vector layer initialized a collection similar to:

```python
Chroma(
    collection_name="restaurant_reviews",
    persist_directory=db_location,
    embedding_function=embeddings
)
```

The purpose of persistence was to avoid rebuilding the entire vector store every time the application started.

The project contained persistent Chroma storage including:

```text
chrome_langchain_db/
    chroma.sqlite3
```

---

## 6. Retrieval Layer

The retrieval architecture exposed a retriever through:

```text
knowledge/vector.py
```

and higher-level search functionality through:

```text
knowledge/knowledge_services.py
```

The resulting conceptual interface was:

```text
User query
   ↓
search(...)
   ↓
retriever
   ↓
Chroma
   ↓
relevant documents
```

---

## 7. Chat Integration

The retrieved knowledge was consumed by:

```text
chat/chat_engine.py
```

The broader dependency chain was:

```text
ChatEngine
    ↓
knowledge_services.search()
    ↓
retriever
    ↓
Chroma
    ↓
retrieved documents
```

This allowed the conversational layer to use domain-specific retrieved context.

---

## 8. Validation Tests

The project was successfully executed using:

```powershell
python -m app
```

The application produced answers to questions grounded in the restaurant-review dataset.

A separate retrieval-oriented test was also executed:

```powershell
python ./test_rag.py
```

The test successfully retrieved multiple documents and generated an answer.

This demonstrated that the retrieval subsystem was operational.

---

## 9. Example Validation Scenario

One of the test questions concerned gluten-free pizza.

The system was able to retrieve relevant restaurant-review documents and use that information in the generated response.

The important verification was not simply the final natural-language response.

The stronger evidence was:

```text
Query
 ↓
Relevant documents retrieved
 ↓
Retrieved content supplied to generation
 ↓
Answer generated
```

---

## 10. Architectural Boundaries Established

Testing helped separate the core RAG system from the newer API layer.

The architecture could be conceptualized as:

```text
                 ┌──────────────────────┐
                 │     API / UI Layer   │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │    Chat Engine      │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │ Knowledge Services  │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │     Retriever       │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │      ChromaDB       │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │ Embedded Documents  │
                 └──────────────────────┘
```

This separation is valuable because a failure in the API layer should not automatically be interpreted as a failure in the RAG layer.

---

## 11. Important Diagnostic Principle

The project demonstrated the value of testing components independently.

Instead of asking only:

> "Does the application work?"

the investigation decomposed the system into:

```text
Can documents be loaded?
        ↓
Can documents be chunked?
        ↓
Can embeddings be generated?
        ↓
Can vectors be persisted?
        ↓
Can relevant vectors be retrieved?
        ↓
Can retrieved context reach the LLM?
        ↓
Can the LLM generate a grounded response?
```

Each question corresponds to a different failure boundary.

---

## 12. Common Failure Modes Considered

A RAG system can fail through several independent mechanisms:

### Ingestion failure

Documents never enter the knowledge base.

### Chunking failure

Documents are split poorly or incorrectly.

### Embedding failure

Embeddings cannot be generated or are inconsistent.

### Persistence failure

Vectors are not stored or cannot be reopened.

### Retrieval failure

Relevant documents are not returned.

### Context integration failure

Retrieved documents are returned but never supplied to the model.

### Generation failure

The model cannot generate a response.

### Grounding failure

The model generates an answer that does not actually follow the retrieved evidence.

---

## 13. General Engineering Lessons

### Lesson 1 — Test behavior, not just startup

A process returning exit code 0 is insufficient evidence that an AI system works.

### Lesson 2 — Observe intermediate artifacts

For RAG systems, useful evidence includes:

* loaded documents,
* chunk counts,
* embedding dimensions,
* stored collection,
* retrieved documents,
* similarity/relevance information,
* final context,
* generated response.

### Lesson 3 — Maintain clear layer boundaries

The retrieval system should be testable without requiring the entire UI/API stack.

### Lesson 4 — Retrieval quality is a first-class subsystem

RAG quality is not solely an LLM problem.

A powerful model cannot compensate for systematically poor retrieval.

---

## 14. Diagnostic Method

```text
Define expected behavior
        ↓
Test ingestion
        ↓
Test chunking
        ↓
Test vector persistence
        ↓
Test retrieval independently
        ↓
Inspect retrieved documents
        ↓
Test context-to-LLM flow
        ↓
Evaluate generated response
        ↓
Test complete application
```

## 15. Future Improvements

Future RAG validation should become more systematic by measuring:

* retrieval precision,
* retrieval recall,
* top-k relevance,
* chunk quality,
* answer faithfulness,
* latency,
* embedding/model consistency,
* persistence/restart behavior.

A mature RAG evaluation suite should eventually distinguish:

```text
Retrieval quality
        +
Context quality
        +
Generation quality
        =
End-to-end RAG quality
```

## 16. Core Principle

The fundamental engineering rule established by this investigation is:

> **Never infer subsystem correctness from end-to-end output alone. Instrument and validate the intermediate stages.**
