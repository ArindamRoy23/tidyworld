# TidyWorld — Technical Design Document

**Version:** 0.2  
**Status:** Draft  
**Last Updated:** 2026-06-05

---

## Table of Contents

1. [Overview](#1-overview)
2. [Terminology](#2-terminology)
3. [System Architecture](#3-system-architecture)
4. [Ingestion Pipeline](#4-ingestion-pipeline)
  - 4.1 Ingest & Chunking Layer
  - 4.2 Information Extraction Agent
  - 4.3 Information Storage
5. [Storage Architecture](#5-storage-architecture)
  - 5.1 Vector Store
  - 5.2 Data Store
  - 5.3 Storage Principles
6. [Tenancy Model](#6-tenancy-model)
7. [Retrieval Architecture](#7-retrieval-architecture)
  - 7.1 Centroid-Based Retriever (Default)
  - 7.2 Retrieval Strategy Configuration
8. [Deduplication & Graph Integrity](#8-deduplication--graph-integrity)
9. [Open Questions](#9-open-questions)

---

## 1. Overview

TidyWorld is a scalable, flexible knowledge graph construction and retrieval system. It ingests arbitrary data sources, extracts structured knowledge (entities and relationships) via an agentic layer, and stores that knowledge in a hybrid vector + data store. The resulting graph can be queried by vector search, graph traversal, SQL, or combinations thereof.

### Design Goals


| Goal                | Description                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Modular**         | Each layer (ingestion, extraction, storage, retrieval) is independently swappable via adapters                    |
| **Extensible**      | New data sources, extraction strategies, and retrieval modes can be added without breaking existing functionality |
| **Fragmented**      | A single global graph is never materialised. Graphs are composed on demand from subgraphs (TidyWorlds)            |
| **Tenantable**      | Data is isolated by tenant at the node and edge level while allowing optional shared public knowledge             |
| **Auto-maintained** | Background services periodically resolve duplicates, prune stale facts, and maintain graph health                 |


### Query Modes Supported

1. Vector similarity search over facts
2. Cypher graph traversal *(TODO: implementation pending)*
3. SQL query over data store
4. Hybrid combinations of the above

---

## 2. Terminology


| Term                  | Definition                                                                                                                                                                               |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fact**              | An atomic piece of information stored as text and as a vector embedding. The fundamental unit of knowledge.                                                                              |
| **Node**              | An entity in the knowledge graph (person, organisation, concept, etc.). Aggregates facts.                                                                                                |
| **Edge**              | A directed relationship between two nodes. Aggregates facts describing that relationship. Has an optional predicate/label.                                                               |
| **TidyWorld**         | A self-contained subgraph derived from a single data point (e.g. one document). Contains nodes and edges extracted from that data point.                                                 |
| **TidyVerse**         | An on-demand composition of one or more TidyWorlds. Represents a virtual view over a subset of the full knowledge graph. Never persisted as a merged structure — composed at query time. |
| **Suspect Duplicate** | A node flagged by the extraction agent as potentially representing the same real-world entity as an existing node. Queued for resolution.                                                |
| **Tenant**            | An isolated consumer of TidyWorld. Tenants do not share graph state unless nodes are tagged as `public`.                                                                                 |


---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        INGESTION PIPELINE                    │
│                                                             │
│  Data Point ──► Ingest & Chunk ──► Extraction Agent ──►    │
│                                        │                    │
│                           ┌────────────┴────────────┐       │
│                           │   Node, Edge, Node       │       │
│                           │   (RDF-style triplets)   │       │
│                           └────────────┬────────────┘       │
│                                        │                    │
│               ┌────────────────────────┴──────────────┐     │
│               │                                       │     │
│        ┌──────▼──────┐                     ┌──────────▼──┐  │
│        │  Data Store  │                     │ Vector Store │  │
│        │  (MongoDB)   │◄────── fact_ids ────│  (Qdrant)   │  │
│        └─────────────┘                     └─────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       RETRIEVAL PIPELINE                     │
│                                                             │
│  Query ──► TidyVerse Resolver ──► Retrieval Strategy ──►   │
│                                         │                   │
│                    ┌────────────────────┤                   │
│                    │                    │                   │
│             Vector Search         Graph Traversal           │
│             (facts/nodes)         (Cypher/SQL)              │
│                    │                    │                   │
│                    └────────────────────┘                   │
│                              │                              │
│                         Ranked Results                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Ingestion Pipeline

### 4.1 Ingest & Chunking Layer

**Pattern:** Adapter

The ingestion layer accepts a data point and produces a set of text chunks, each of which will be processed by the extraction agent. Any data source can be supported by implementing the `IngestAdapter` interface.

#### Interface

```python
class IngestAdapter(ABC):
    @abstractmethod
    def ingest(self, source: DataSource) -> List[Chunk]:
        """
        Accept a raw data source and return an ordered list of text chunks.
        Each chunk carries metadata about its origin (page, section, offset, etc.)
        """
        pass
```

#### Default Adapter: PDF via Docling

- **Extraction:** Docling extracts text, tables, and structure from PDF.
- **Chunking:** Semantic chunking by section/paragraph with configurable max token size.
- **Metadata carried per chunk:** `source_id`, `page_number`, `section_heading`, `chunk_index`, `char_offset`.

#### Planned Adapters


| Source                  | Status        |
| ----------------------- | ------------- |
| PDF                     | ✅ Implemented |
| CSV                     | Planned       |
| JSON                    | Planned       |
| Web page                | Planned       |
| Audio transcript        | Future        |
| Multimodal (image+text) | Future        |


Each document ingested becomes one **TidyWorld**. The TidyWorld is the unit of graph fragmentation.

---

### 4.2 Information Extraction Agent

**Pattern:** Adapter

The extraction layer consumes chunks and produces a structured graph (nodes + edges) as output. The default implementation uses a LangGraph multi-agent system. Custom implementations can be swapped in per business use case.

#### Interface

```python
class ExtractionAdapter(ABC):
    @abstractmethod
    def extract(self, chunks: List[Chunk], context: ExtractionContext) -> GraphOutput:
        """
        Given chunks from a document, extract nodes and edges.
        ExtractionContext carries tenant_id, existing node index hints, and config.
        """
        pass
```

#### Default Adapter: LangGraph Multi-Agent

The default extraction adapter implements a hierarchical agent system.

##### Agent Hierarchy

```
Orchestrator Agent
├── Node Creation Agent
│   └── Decides whether to create a new node or reference an existing one.
│       Uses "Search Similar Nodes" tool before any creation decision.
├── Node Information Agent
│   └── Enriches an existing or newly created node with facts from the current chunk.
└── Edge Information Agent
    └── Identifies relationships between nodes and attaches facts to edges.
        Determines edge predicate (relationship type) from business config.
```

##### Agent Tools


| Tool                        | Description                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| `search_similar_tidyworlds` | Vector search over existing TidyWorlds to find related documents already in the graph              |
| `search_similar_nodes`      | Vector/keyword search over existing nodes to surface potential duplicates before creation          |
| `mark_suspect_duplicate`    | Flags a node pair as potentially duplicate without blocking ingestion; queues for async resolution |
| `update_state_graph`        | Writes nodes or edges to the in-memory state graph that will be persisted at the end of extraction |


##### Extraction Output Schema

```json
{
  "nodes": [
    {
      "node_id": "tmp_001",
      "facts": ["Apple Inc. was founded in 1976.", "Apple is headquartered in Cupertino, CA."],
      "db_node_id": null
    },
    {
      "node_id": "tmp_002",
      "facts": ["Steve Jobs was a co-founder of Apple."],
      "db_node_id": "existing_node_abc123"
    }
  ],
  "edges": [
    {
      "start_node_id": "tmp_002",
      "end_node_id": "tmp_001",
      "predicate": "co_founded",
      "facts": ["Steve Jobs co-founded Apple Inc. in 1976 alongside Steve Wozniak."]
    }
  ]
}
```

**Notes on schema:**

- `node_id` is a temporary ID scoped to this extraction run. It is resolved to a `db_node_id` during storage.
- `db_node_id` is populated when the agent determines a node already exists in the graph.
- `predicate` on edges is optional by default. Business configurations can enforce a constrained vocabulary of predicates (e.g. `invested_in`, `employed_by`, `located_in`).

##### Cost & Latency Characteristics

The multi-agent loop issues multiple LLM calls per chunk. For a 100-page document this may produce 5–15 LLM calls per chunk depending on entity density. This is accepted as a design trade-off at this stage.

Mitigation strategies under consideration:

- **Node lookup caching** within an ingestion run to avoid redundant similarity searches for repeated entities.
- **Batch similarity search** across all candidate entities in a chunk before spawning sub-agents.
- **Edge compute deployment** for client-side ingestion in latency-sensitive production scenarios.

---

### 4.3 Information Storage

After extraction, the graph output is persisted across the Vector Store and Data Store. See Section 5 for full schema and storage principles.

**Storage flow:**

```
GraphOutput
    │
    ├── For each fact (node facts + edge facts):
    │       1. Embed fact text → vector
    │       2. Write to Vector Store → receive fact_id
    │
    └── For each node and edge:
            3. Write to Data Store with fact_ids (not fact text)
            4. Write TidyWorld document linking all nodes and edges
```

---

## 5. Storage Architecture

### Core Principle

> If text → store in Vector Store.  
> All else → store in Data Store.  
> The Data Store always references the Vector Store by `fact_id`. The Vector Store never references the Data Store.

Both stores use the adapter pattern and can be replaced with alternative implementations.

---

### 5.1 Vector Store

**Default Implementation:** Qdrant

The Vector Store holds a single collection: `facts`. Every atomic piece of knowledge (a sentence or short paragraph extracted from a chunk) is stored here as a vector alongside its raw text.

#### Schema

```
Collection: facts
{
    fact_id:      int           -- Unique identifier; referenced by Data Store
    text:         str           -- Raw text of the fact
    text_vector:  List[float]   -- Embedding of the fact text
    tenant_id:    str           -- Tenant scope; "public" for shared facts
    node_id:      str | null    -- The node this fact belongs to (for node-scoped search)
    edge_id:      str | null    -- The edge this fact belongs to, if applicable
    created_at:   datetime
}
## This is data duplication, but required for search (tenant/node/edge...)
```

**Why store `node_id` on facts?**  
This enables efficient node-level vector aggregation (e.g. centroid computation) without a join back to the Data Store. See Section 7 for retrieval usage.

---

### 5.2 Data Store

**Default Implementation:** MongoDB

The Data Store holds graph structure, metadata, and all non-text data. It never stores raw text — only `fact_id` references into the Vector Store.

#### Collections

`**nodes`**

```
{
    node_id:       str           -- Stable, globally unique ID (UUID recommended)
    tenant_id:     str           -- Tenant scope
    fact_ids:      List[int]     -- References into Vector Store facts collection
    labels:        List[str]     -- Optional ontology labels (e.g. ["Person", "Founder"])
    confidence:    float         -- Aggregate confidence score (0.0–1.0)
    created_at:    datetime
    updated_at:    datetime
    source_world_ids: List[int]  -- Which TidyWorlds contributed to this node
}
```

`**edges**`

```
{
    edge_id:         str
    start_node_id:   str
    end_node_id:     str
    predicate:       str | null  -- Relationship type (e.g. "invested_in", "employed_by")
    fact_ids:        List[int]
    tenant_id:       str
    confidence:      float
    created_at:      datetime
    updated_at:      datetime
}
```

`**tidyworlds**`

```
{
    tidy_world_id:   str
    tenant_id:       str
    node_ids:        List[str]
    edge_ids:        List[str]
    source_type:     str         -- e.g. "pdf", "csv", "json"
    source_ref:      str         -- Path, URL, or identifier of original data point
    created_at:      datetime
    updated_at:      datetime
    metadata:        dict        -- Arbitrary KV pairs (title, author, tags, etc.)
}
```

`**tidyverses**`

```
{
    tidy_verse_id:      str
    tenant_id:          str
    tidy_world_ids:     List[str]   -- Constituent TidyWorlds
    description:        str | null  -- Optional human label
    created_at:         datetime
    metadata:           dict
}
```

`**suspect_duplicates**`

```
{
    record_id:                str
    node_id:                  str      -- Candidate node
    suspect_duplicate_node_id: str     -- Node it may duplicate
    similarity_score:         float    -- Cosine similarity at time of flagging
    flagged_at:               datetime
    flagged_by:               str      -- "agent" | "periodic_service" | "user"
    status:                   str      -- "pending" | "merged" | "dismissed"
    resolved_at:              datetime | null
    resolved_by:              str | null
}
```

---

### 5.3 Storage Principles

- **Immutable fact log:** Facts are never deleted, only tombstoned (`is_active: false`). Graph corrections remain auditable.
- **Reference direction:** Data Store → Vector Store (one-way). No fact in Qdrant references MongoDB documents.
- **Node ID stability:** Once a `node_id` is issued, it never changes. Merges are handled by pointing the losing node's `node_id` to the winning node via a redirect record, preserving referential integrity.

---

## 6. Tenancy Model

### Model: Partitioned Graph with Shared Public Layer

Every node, edge, and TidyWorld carries a `tenant_id`. All queries are scoped to `tenant_id IN [current_tenant, "public"]`.

The `"public"` tenant is a curated shared layer. Public nodes represent well-known entities (major organisations, widely known people, geographic locations, etc.) that all tenants can read. No tenant can write to the public layer directly — promotion to `"public"` is an administrative action.

### Tenant Isolation Rules


| Operation                   | Rule                                           |
| --------------------------- | ---------------------------------------------- |
| Read own nodes              | Always allowed                                 |
| Read public nodes           | Always allowed                                 |
| Read another tenant's nodes | Not allowed                                    |
| Write to public layer       | Admin only                                     |
| Compose a TidyVerse         | Can combine own TidyWorlds + public TidyWorlds |


### TidyVerse Scoping

A TidyVerse is always constructed within a tenant scope:

```python
def compose_tidyverse(
    tenant_id: str,
    world_ids: List[str],
    include_public: bool = True
) -> TidyVerse:
    allowed_worlds = get_worlds_for_tenant(tenant_id, include_public)
    selected = [w for w in world_ids if w in allowed_worlds]
    return TidyVerse(tidy_world_ids=selected, tenant_id=tenant_id)
```

### Metadata on Data Points

Each TidyWorld carries the ingesting tenant's `tenant_id` as a top-level field (not buried in `metadata`). This enables efficient index-level filtering in both MongoDB and Qdrant without parsing nested documents.

---

## 7. Retrieval Architecture

> **Note:** The retrieval layer is under active design. This section describes the default centroid-based retriever. Additional strategies will be added.

### 7.1 Centroid-Based Retriever (Default)

#### Concept

Each node in the knowledge graph has one or more facts stored as vectors in the Vector Store. The **centroid** of a node is the mean of all its fact vectors. At query time, the query is embedded and compared against node centroids to rank nodes by relevance.

This is the most balanced default because:

- It represents the full information content of a node, not just one fact.
- It is not biased toward the most recent or most extreme fact.
- It degrades gracefully as new facts are added (centroid shifts incrementally).

#### Algorithm

```
QUERY TIME:
1. Embed query text → query_vector

2. For each candidate node in scope (tenant + public):
   a. Fetch all fact_ids for node from Data Store
   b. Fetch all fact vectors from Vector Store (batch)
   c. Compute centroid = mean(fact_vectors)

3. Score each node: cosine_similarity(query_vector, centroid)

4. Rank nodes by score, apply top-k filter

5. For top-k nodes:
   a. Fetch all fact texts for node
   b. Fetch adjacent edges and their facts (optional: for graph context)

6. Return ranked nodes with their facts and optional graph context
```

#### Implementation

```python
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class RetrievedNode:
    node_id: str
    score: float
    facts: List[str]
    centroid: np.ndarray
    adjacent_edges: Optional[List[Dict]] = None


class CentroidRetriever:
    """
    Default retriever. Ranks nodes by cosine similarity between
    the query vector and the centroid of each node's fact vectors.
    """

    def __init__(
        self,
        vector_store,       # VectorStoreAdapter
        data_store,         # DataStoreAdapter
        embed_fn,           # Callable[[str], np.ndarray]
        top_k: int = 10,
        include_edges: bool = False,
    ):
        self.vector_store = vector_store
        self.data_store = data_store
        self.embed_fn = embed_fn
        self.top_k = top_k
        self.include_edges = include_edges

    def retrieve(
        self,
        query: str,
        tenant_id: str,
        world_ids: Optional[List[str]] = None,
    ) -> List[RetrievedNode]:
        """
        Retrieve the top-k most relevant nodes for a query,
        scoped to the given tenant and optional TidyVerse (world_ids).
        """
        query_vector = self.embed_fn(query)

        # Fetch candidate nodes scoped to tenant (+ public)
        nodes = self.data_store.get_nodes(
            tenant_ids=[tenant_id, "public"],
            world_ids=world_ids,
        )

        scored_nodes = []
        for node in nodes:
            centroid = self._compute_centroid(node["fact_ids"])
            if centroid is None:
                continue
            score = self._cosine_similarity(query_vector, centroid)
            scored_nodes.append((node, centroid, score))

        # Sort descending by score, take top-k
        scored_nodes.sort(key=lambda x: x[2], reverse=True)
        top_nodes = scored_nodes[: self.top_k]

        results = []
        for node, centroid, score in top_nodes:
            facts = self.vector_store.get_fact_texts(node["fact_ids"])
            edges = None
            if self.include_edges:
                edges = self.data_store.get_edges_for_node(node["node_id"])
            results.append(
                RetrievedNode(
                    node_id=node["node_id"],
                    score=score,
                    facts=facts,
                    centroid=centroid,
                    adjacent_edges=edges,
                )
            )

        return results

    def _compute_centroid(self, fact_ids: List[int]) -> Optional[np.ndarray]:
        """
        Fetch fact vectors for a node and return their mean.
        Returns None if no facts exist.
        """
        if not fact_ids:
            return None
        vectors = self.vector_store.get_vectors(fact_ids)
        if not vectors:
            return None
        return np.mean(vectors, axis=0)

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
```

#### Centroid Maintenance

Node centroids can be precomputed and cached to avoid recomputing per query. The centroid is invalidated whenever a new fact is added to a node.

```python
# Incremental centroid update when a new fact is added
def update_centroid_incremental(
    current_centroid: np.ndarray,
    current_fact_count: int,
    new_fact_vector: np.ndarray,
) -> np.ndarray:
    """
    O(1) centroid update without reloading all fact vectors.
    new_centroid = (current_centroid * n + new_vector) / (n + 1)
    """
    n = current_fact_count
    return (current_centroid * n + new_fact_vector) / (n + 1)
```

Cached centroids can be stored as a field on the node document in MongoDB, updated atomically on each fact write.

---

### 7.2 Retrieval Strategy Configuration

The retriever is pluggable. The following strategies are planned:


| Strategy               | Description                                          | Best For                          |
| ---------------------- | ---------------------------------------------------- | --------------------------------- |
| **Centroid** (default) | Mean of all fact vectors                             | Balanced, general-purpose         |
| **Latest**             | Most recently added fact vector                      | News, time-sensitive knowledge    |
| **Rarest**             | Fact vector with lowest average similarity to others | Unique/distinctive entity recall  |
| **Closest**            | Most similar individual fact vector (no aggregation) | High-precision single-fact lookup |
| **Max-pool**           | Component-wise maximum across fact vectors           | Broad topic coverage              |


Strategy is set at TidyVerse or query level:

```python
results = retriever.retrieve(
    query="Who invested in OpenAI?",
    tenant_id="acme_corp",
    strategy="centroid",   # or "latest", "rarest", "closest"
    world_ids=["world_001", "world_002"],
)
```

---

## 8. Deduplication & Graph Integrity

### Ingestion-Time Resolution (Primary)

Before creating a new node, the Node Creation Agent searches for similar existing nodes. If similarity exceeds a threshold, the agent resolves to the existing `db_node_id` instead of creating a new node. If uncertain, it flags a `Suspect_duplicate` record and proceeds with creation.

This is probabilistic. It is expected to catch the majority of duplicates but not all.

### Periodic Resolution Service (Safety Net)

A background service runs on a configurable schedule and:

1. Scans all `suspect_duplicates` with `status = "pending"`.
2. For each candidate pair, recomputes similarity using current fact vectors (which may have grown since flagging).
3. Applies merge if similarity exceeds the merge threshold; dismisses if below the dismiss threshold; leaves pending if in between.

**Merge operation:**

- All `fact_ids` from the losing node are appended to the winning node.
- All edges referencing the losing `node_id` are repointed to the winning `node_id`.
- The losing node is tombstoned (`is_active: false`) with a `merged_into` pointer.
- Centroid cache for the winning node is invalidated.

### Node ID Stability Under Merges

Merges never delete a `node_id`. A redirect table maps deprecated node IDs to their canonical successor. Queries resolve deprecated IDs transparently.

```
node_redirects: {
    deprecated_node_id: str
    canonical_node_id:  str
    merged_at:          datetime
}
```

---

## 9. Open Questions

### Design

1. **Predicate vocabulary:** Should predicates be a free-text field or constrained to an enum per tenant? If enum, who manages the vocabulary and what happens when new relationship types are needed? How do predicates interact across tenants that share public nodes?
2. **Centroid cache invalidation at scale:** If a high-cardinality node (e.g. "Google") accumulates thousands of facts across many TidyWorlds, recomputing or caching the centroid becomes expensive. What is the right caching and invalidation strategy? Should there be a max-fact cap per node, with older facts downweighted?
3. **Cross-tenant entity identity:** If Tenant A and Tenant B both ingest information about the same real-world entity, should there be a mechanism to link their respective private nodes to a shared public node? Who triggers this? Is it automated or administrative?
4. **TidyVerse persistence:** Currently TidyVerses are defined by `tidy_world_ids`. Should named/persistent TidyVerses be a first-class product concept (saved views), or always ephemeral? What are the implications for caching retrieval results?
5. **Edge direction and symmetry:** Are all edges directed? How should symmetric relationships (e.g. "is_sibling_of") be handled — one directed edge, two directed edges, or an undirected edge type?

### Operational

1. **Ingestion cost baseline:** What is the actual LLM call count and $ cost per page for the default multi-agent extractor? No empirical measurement exists yet. Needs a benchmarking run before production planning.
2. **Qdrant vs. alternatives for node-level aggregation:** Qdrant is optimised for point-level similarity search. Aggregating vectors by `node_id` at query time (for centroid computation) may not be efficiently supported. Should centroid vectors be precomputed and stored as a separate collection?
3. **Merge conflict resolution:** When two nodes are merged, their facts may be contradictory (e.g. different founding dates for a company). There is currently no contradiction detection or resolution. Should contradictory facts be flagged? Downweighted? Resolved by recency?
4. **Schema migration:** As the schema evolves, how will existing MongoDB documents and Qdrant vectors be migrated? No migration strategy exists yet.

### Product

1. **Cypher query layer:** The overview lists Cypher as a supported query mode, but no graph database is in the stack. Is the intent to add Neo4j or a similar system alongside MongoDB, or to implement a Cypher-to-MongoDB translator? This is a significant architectural decision.
2. **Auto-maintenance scope:** "Auto-maintained" is a design goal but currently only covers deduplication. What else does auto-maintenance include? Candidates: stale fact detection, re-embedding on model upgrade, dangling edge cleanup, confidence score decay for old facts.
3. **Human-in-the-loop for suspect duplicates:** The current model is fully automated. For high-stakes use cases, a human review queue for suspect duplicates may be required. Is there a product surface for this?

---

# Operational Details

## Repo Structure:

```
tidyworld/
│
├── extractor/
│   ├── pipeline.py              # Orchestrates ingest → extract → store
│   │
│   ├── ingest/
│   │   ├── base.py
│   │   └── pdf.py
│   │
│   ├── extract/
│   │   ├── base.py
│   │   └── lg_multi_agent/
│   │       ├── __init__.py
│   │       ├── agent.py
│   │       ├── nodes.py
│   │       └── tools.py
│   │
│   └── store/
│       ├── vector/
│       │   ├── base.py
│       │   └── qdrant.py
│       └── data/
│           ├── base.py
│           └── mongo.py
│
├── retriever/                   # placeholder
│   └── .gitkeep
│
├── models/
│   ├── chunk.py
│   ├── graph.py
│   └── tidyworld.py
│
└── config.py
```

