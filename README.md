# TidyWorld Project

TidyWorld is a scalable and flexible knowledge graph construction system designed to build a knowledge graph from your data. It serves as a robust knowledge layer for any application.

## 🔍 Query Capabilities
Any TidyWorld project can be queried in multiple ways to suit your application's needs:
- **Vector Search**
- **SQL Query**
- **Combined Search** (a combination of the above methods)

## ✨ Design Principles
TidyWorld is built from the ground up with the following principles in mind:
- **Modular:** Components can be easily swapped or updated.
- **Extensible:** Easily add new features and integrations.
- **Fragmented:** Designed to handle distributed data.
- **Tenantable:** Supports multi-tenant architectures.
- **Auto-maintained:** Reduces manual overhead for upkeep.

## 🧠 Core Concepts

### What is a TidyWorld?
A **TidyWorld** is a single unit of knowledge for a specific data point. It combines three core technologies:
1. **Knowledge Graph:** Stores the entities and the relationships between them.
2. **Vector Database:** Stores the embeddings of the data points for semantic retrieval.
3. **NoSQL Database:** Stores the metadata associated with the data points.

### What is a TidyVerse?
A **TidyVerse** is a collection of TidyWorlds that are related to each other. It acts as the primary container used to store and manage the data for a single application.

### Agents in TidyWorld
**Agents** are the active components required to build and maintain the TidyWorld. They:
- Are highly configurable based on specific application needs.
- Manage the core business logic.
- Handle the creation, updating, and deletion of nodes, edges, and factoids.

### How Does TidyWorld Scale?
TidyWorld achieves massive scalability through a unique architecture:
- **Granular Storage:** Each data point is represented and stored as a separate TidyWorld.
- **Shared Infrastructure:** A common vector database and NoSQL database are used across all TidyWorlds.
- **Computed Knowledge Graphs:** Instead of being statically stored, the Knowledge Graph (KG) is computed on demand. This separation of storage and computation allows for a highly scalable and flexible system.
