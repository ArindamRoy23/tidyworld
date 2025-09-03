# TidyWorld: Agentic Self-Maintaining Knowledge Graph

> **⚠️ WORK IN PROGRESS**: This project is under active development and the features described may not be fully implemented yet.

TidyWorld reimagines knowledge graph construction by creating a dynamic, intelligent system that automatically evolves its understanding of data through agentic processes. Unlike traditional knowledge graphs that require manual schema definition and static extraction rules, TidyWorld uses AI agents to continuously learn, adapt, and maintain both the data structure and content quality.

## 🌟 Project Vision

### Core Philosophy
TidyWorld addresses fundamental limitations in current knowledge graph systems:
- **Structured Extraction** Unstructured extraction leads to enourmous duplication and reduces usability.
- **Queryability** Voluminous textual data can be quried fast and easyG
- **Knowledge Updation and Provenance** Keep each peice of information trackable to the document and its metadata.
- **Flexible** Add business logic to extraction/updation
- **Linkages** Different graph entities can be linked to a diverse range of data storages.

### Key Innovations

#### 1. **Agentic Schema Evolution**
Instead of manually defining rigid schemas, TidyWorld uses AI agents to:
- Automatically discover entity types and their properties from documents
- Evolve schemas as new information patterns emerge
- Maintain backward compatibility while adding new fields and relationships
- Use semantic field matching to intelligently assign extracted data to appropriate schemas

#### 2. **Factoid-Based Versioning System**
TidyWorld stores information as atomic, versioned factoids that preserve:
- **Complete change history** - Track how entity attributes evolve over time
- **Source attribution** - Link every piece of information to its originating document
- **Conflict resolution** - Handle contradictory information from multiple sources
- **Temporal queries** - Reconstruct entity states at any point in time

#### 3. **Intelligent Deduplication with Separate Processing Paths**
The system routes extracted entities through specialized agentic paths:
- **Creation Path**: For genuinely new entities requiring fresh graph nodes
- **Update Path**: For adding information to existing entities
- **Merge Path**: For combining duplicate entities discovered across documents
- **Conflict Path**: For handling uncertain cases that need human review or additional analysis

#### 4. **Hybrid Storage Architecture**
TidyWorld coordinates between multiple storage systems:
- **NoSQL Database**: Stores versioned factoids with complete audit trails
- **Knowledge Graph**: Maintains current canonical entity views and relationships
- **Vector Database**: Enables semantic search and schema matching
- **Event-Driven Sync**: Ensures consistency across all storage layers

## 🏗️ Technical Architecture

### System Overview
```
*TO FILL*
```

### Services

#### Chunk Extraction Service
Made to extract chunks and save it in memory

#### Data Modeling Service
Made for updating/creating datamodels  (Nodes and Entities)

#### State Manager Service
Made for managing state and operations
- insert
-upsert
-delete

### Hybrid storage manager


### Storages

#### VectorDB storage
- Create collection
- Delete collection
- Create Item

#### NoSQLDB storage

#### Graph storage

### Key Technical Decisions

#### **Why Factoids Over Traditional Entity Storage?**
- **Granular Provenance**: Know exactly which document contributed each piece of information
- **Conflict Management**: Handle contradictory information without data loss
- **Temporal Analysis**: Track how entity attributes change over time
- **Source Quality**: Weight information based on document reliability and recency

#### **Why Hybrid Schema Approach?**
- **Human Accessibility**: YAML files enable non-technical schema editing
- **Runtime Performance**: Database storage provides millisecond schema lookups
- **Semantic Intelligence**: Vector embeddings enable smart schema selection
- **Version Control**: Git integration for schema change management

#### **Why Separate Processing Paths?**
- **Specialized Logic**: Different algorithms for creation vs. updates vs. merges
- **Performance Optimization**: Avoid expensive deduplication for clearly new entities
- **Quality Control**: Route uncertain cases to human reviewers
- **Scalability**: Parallel processing of different entity types

## 🔧 Implementation Status

### Repository Structure
```
tidyworld/
├── _tidyworld.py              # Main orchestrator class
├── _types.py                  # Core type definitions
├── _models.py                 # Pydantic models for structured output
├── _utils.py                  # Utility functions
├── _services/                 # Pluggable service implementations
│   ├── _base.py              # Service interface definitions
│   └── _chunk_extraction.py  # Contextual chunking implementation
├── _schemas/                  # Schema management system
│   └── _base.py              # Schema registry and evolution logic
├── _storage/                  # Storage abstraction layer
│   └── _base.py              # Multi-database coordination
├── _agents/                   # Agentic processing components
│   └── _base.py              # Agent framework and interfaces
└── _llm/                     # Language model integration
    └── ...                   # LLM service implementations
```

### Current Implementation Phase
- ✅ **Foundation**: Core architecture and service interfaces defined
- 🔄 **In Progress**: Agentic extraction service and schema management
- 📋 **Next**: Factoid storage system and deduplication logic
- 🔮 **Future**: Production optimizations and user interfaces

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Supported vector database (Qdrant, Weaviate, or Chroma)
- NoSQL database (MongoDB, ArangoDB, or Cassandra)
- Knowledge graph database (Neo4j, ArangoDB, or NetworkX)

### Basic Usage
```python
from tidyworld import TidyWorld

# Initialize with your preferred storage backends
tidy = TidyWorld(
    working_dir="./knowledge_graph",
    vector_storage="qdrant://localhost:6333",
    nosql_storage="mongodb://localhost:27017/tidyworld",
    graph_storage="neo4j://localhost:7687"
)

# Ingest documents - schemas evolve automatically
await tidy.insert([
    "John Doe works at Microsoft as a Senior Engineer.",
    "Jane Smith is the CEO of TechCorp, located in San Francisco."
])

# Query with full provenance
result = await tidy.query(
    "Who works at technology companies?",
    include_provenance=True,
    temporal_context="last_6_months"
)
```

### Model Configuration
```python
from pydantic import BaseModel, Field
from tidyworld._types import TSchemaSource, TSchemaDefinition

# Define a schema source
source = TSchemaSource(
    name="user_models",
    source_type="json",
    location="/path/to/models.json",
    metadata={"version": "1.0"}
)

# Define a model with identifiers
class Person(BaseModel):
    name: str = Field(..., identifier=True)
    email: str = Field(..., identifier=True)
    age: int | None = None
    occupation: str | None = None

# Create schema definition
person_schema = TSchemaDefinition(
    model_name="Person",
    schema_definition={
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "optional": True},
        "occupation": {"type": "string", "optional": True}
    },
    identifiers=["name", "email"],
    metadata={
        "version": "1.0",
        "category": "user",
        "description": "Person entity with professional attributes"
    }
)
```

## 🌟 Differentiating Features

### vs. LightRAG
- **Dynamic schemas** instead of static entity types
- **Factoid versioning** instead of entity overwrites
- **Agentic processing** instead of fixed extraction rules
- **Multi-database coordination** instead of single storage backend

### vs. Traditional Knowledge Graphs
- **Self-evolving structure** that adapts to new data patterns
- **Complete information provenance** with source attribution
- **Intelligent conflict resolution** for contradictory information
- **Temporal analysis capabilities** for tracking changes over time

### vs. Fast-GraphRAG
- **Schema-aware extraction** with validation and evolution
- **Granular factoid storage** instead of document-level chunks
- **Business logic integration** through pluggable agents
- **Multi-modal storage** for different data access patterns

## 🎯 Use Cases

### Enterprise Knowledge Management
- **Document Processing**: Automatically extract and organize information from contracts, reports, and communications
- **Regulatory Compliance**: Maintain audit trails for all information sources and changes
- **Knowledge Discovery**: Find connections between entities across disparate document sources

### Research and Academia
- **Literature Analysis**: Build knowledge graphs from academic papers with full citation tracking
- **Temporal Studies**: Track how concepts and relationships evolve over time
- **Cross-Domain Integration**: Merge knowledge from multiple research domains intelligently

### Legal and Financial Services
- **Due Diligence**: Extract and verify entity information from multiple document sources
- **Risk Assessment**: Track entity relationships and flag potential conflicts of interest
- **Compliance Monitoring**: Maintain detailed provenance for regulatory reporting

## 🛣️ Roadmap

### Phase 1: Core Platform (Q1 2024)
- Complete agentic extraction service implementation
- Robust factoid storage and versioning system
- Basic schema evolution with human oversight
- Production-ready hybrid storage coordination

### Phase 2: Intelligence Layer (Q2 2024)
- Advanced conflict resolution algorithms
- Automated schema evolution with confidence thresholds
- Performance optimizations for large-scale deployments
- Comprehensive monitoring and observability tools

### Phase 3: User Experience (Q3 2024)
- Web-based schema management interface
- Visual knowledge graph exploration tools
- RESTful and GraphQL APIs for integration
- Extensive documentation and tutorials

### Phase 4: Enterprise Features (Q4 2024)
- Multi-tenant architecture with workspace isolation
- Advanced security and access control
- Horizontal scaling for massive document collections
- Integration with popular enterprise tools

## 🤝 Contributing

TidyWorld is designed to be extensible and community-driven. Key areas for contribution:

- **Storage Backends**: Implement new database connectors
- **Extraction Agents**: Build domain-specific processing logic
- **Schema Definitions**: Contribute common entity type schemas
- **Performance Optimizations**: Improve scalability and efficiency

## 📄 License

Apache License 2.0 - See LICENSE file for details.

## 🙏 Acknowledgments

TidyWorld builds upon ideas from:
- **LightRAG**: Knowledge graph construction from documents
- **Fast-GraphRAG**: Modular architecture for graph-based RAG
- **Neo4j**: Graph database best practices
- **Pydantic**: Schema validation and evolution patterns

---

*TidyWorld represents the next evolution in knowledge graph technology - where artificial intelligence doesn't just extract information, but intelligently organizes, validates, and maintains the entire knowledge structure over time.*
