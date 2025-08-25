# TidyWorld

TidyWorld is an agentic self-maintaining knowledge graph system designed to intelligently organize, validate, and link information from various documents and data sources.

## Overview

TidyWorld reimagines document-centric knowledge management by creating a dynamic, self-evolving graph structure that maintains data integrity while preserving source context. The system employs NoSQL database architecture for flexible data storage and intelligent schema evolution.

## Key Features

### 1. NoSQL-Based Graph Storage
- OLAP-style architecture supporting heterogeneous data types
- Flexible querying across different entity types and relationships
- Optimized for complex graph traversals and pattern matching

### 2. Intelligent Schema Evolution
- Dynamic Pydantic-based data validation for all nodes and edges
- Automated schema updates based on document analysis
- Self-learning entity recognition and attribute mapping
- Examples of entity types:
  ```python
  class Person:
      name: str
      age: Optional[int]
      phone: Optional[str]
      # Dynamically expanded based on encountered data

  class Place:
      name: str
      latitude: Optional[float]
      longitude: Optional[float]
      # Dynamically expanded based on encountered data
  ```

### 3. Document-Centric Provenance
- Every piece of information is linked to its source document
- Queryable document metadata at the retrieval level
- Complete traceability of information origins
- Support for conflict resolution and data versioning

### 4. Agentic Maintenance
- Autonomous agents for:
  - Schema evolution and validation
  - Entity completion from external sources
  - Relationship inference
  - Data quality monitoring
- Continuous learning from new documents and interactions

## Architecture

The system is built on three main pillars:
1. **Storage Layer**: NoSQL database optimized for graph operations
2. **Validation Layer**: Dynamic Pydantic models for data integrity
3. **Agent Layer**: Autonomous processes for system maintenance and evolution

## Use Cases

- Knowledge Management Systems
- Document Analysis and Linking
- Intelligent Information Retrieval
- Automated Knowledge Base Construction
- Data Lineage Tracking

## Technical Stack

- **Database**: NoSQL (Graph-optimized)
- **Data Validation**: Pydantic
- **Agent Framework**: To be determined
- **API Layer**: To be determined

## Project Status

🚧 Under Development

## License

[To Be Determined]