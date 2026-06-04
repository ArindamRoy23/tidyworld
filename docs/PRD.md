## What is TidyWorld project?

Tidyworld project is a scalable and flexible knowledge graph construction system that allows you to build a knowledge graph from your data. It is meant to serve as a knowledge layer for any application. Any tidyworld procect can be:
    1. Queried by vector search
    2. Queried by Cypher graph search
    3. Queried by SQL query
    4. Queried by a combination of the above

Further more, TidyWorld project is designed to be:
    1. Modular
    2. Extensible
    3. Fragmented
    4. Tenantable
    5. Auto-maintained

## Core Concepts

### What is a TidyWorld? 
A tidyworld is a combination of a knowledge graph, a vector database, and a noSQL database for a single data point. The knowledge graph is used to store the entities and relationships between them. The vector database is used to store the embeddings of the data points. The noSQL database is used to store the metadata of the data points. A tidyworld is a single unit of knowledge.

### What is a TidyVerse? 
A tidyverse is a collection of tidyworlds that are related to each other. It is used to store the data for a single application. It is a collection of tidyworlds that are related to each other. It is used to store the data for a single application.

### What are agents in TidyWorld?
Agents in tidyworld are required to build/maintain the tidyworld. These agents can be configured based on the application needs. These manage the business logic of node/edge/factoid creation/updation/deletion.

### How does tidyworld scale? 
Each data point is stored in a separate tidyworld. A common vector and noSQL database is used to store the data for all tidyworlds, but the KG is computed, not stored. This allows for a scalable and flexible system.

