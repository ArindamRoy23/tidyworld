# TidyWorld Technical Design Document

## Overview

TidyWorld is a scalable and flexible knowledge graph construction system that allows you to build a knowledge graph from your data. It is meant to serve as a knowledge layer for any application. Any tidyworld project can be:
    1. Queried by vector search
    2. Queried by Cypher graph search #TODO: Figure how to enable this
    3. Queried by SQL query
    4. Queried by a combination of the above

Further more, TidyWorld project is designed to be:
    1. Modular
    2. Extensible
    3. Fragmented
    4. Tenantable
    5. Auto-maintained


## Ingestion Process

### Ingest and chunking
This is designed in the adapter design pattern. Any data source can be ingested and chunked into tidyworlds. For now, we will support the following data sources:
    1. PDF 
### Default ingest and chunking adapter
For PDF, we will use docling to extract the text from the PDF. For chunking, we will use the default chunking service. In future, we will support other data sources like CSV, JSON, etc. Multimodal data sources will be supported in the future.
Each document thus becomes a tidyworld. All metadata associated to a document can be stored in the 

#TODO: Add more data sources and chunking services.

### Information extraction agent
This layer is for extracting the entities and relationships from the tidyworlds. It is designed in the adapter design pattern. You can plug in your own information extraction service to extract the entities and relationships to form the tidyworld. 
This project implements a default information extraction agent adapter that uses langgraph agents. However, you can plug in your own information extraction service to extract the entities and relationships to form the tidyworld. This is driven by the business logic of the application.

### Default information extraction agent adapter
Default adapter implements langgraph agents Langgraph.
The execiting agent cretes a graph in state and gives it as output. 
Agent design: 
- Orchastrator agent: Holds the core business logic to extract.
    * Node creation agent: Thinks about if a node really need to be created, or already exists.
    * Node information agent: Add facts to a node  
    * Edge information agent: Add facts between two nodes  

The tools built for this agent are:
    1. Search similar tidyworlds: For the given document, search for similar tidyworlds in the vector database.
    2. Search similar nodes: For a given text, vector/keyword search the nodes in the knowledge graph.
    3. Mark suspect duplicate nodes: When unsure if a node is a duplicate, mark it as suspect duplicate.
    4. Update state graph: update nodes or edges in state 

Output
```
{
    nodes: [
        {
            node_id: Str | Temp ID for creation
            facts: List[str] | list of fact
            db_node_id: Optional[str] | In case already in DB, fill ID
        }
    ],
    edges: [
        {
            start_node_id:Str | Temp ID 
            end_node_id:  Str | Temp ID 
            facts: List[str] | list of facts
        }
    ]

}
```

### Information storage
Information is stored in two stores:
1. Vector Store
2. Data Store

Core principal of storage is: 
If text, store in vector store, all else in data store. 
Always point data store to vector store, never the other way round.
Both the stores are in an adapter pattern, and can be configured to required underlying implimentation.
Vector store necessarily needs to be a vector enabled DB, however the data store can be a range of implimentations, like SQL DB, NoSQL DB, SparkDF, KV Stores, etc 

### Default information storage adapters
1. Vector Store: Qdrant
There is a single table called facts implemented in Qdrant. All facts get stored in this table as a vector. The text of the vector is also stored in this table. The ID of this is used in te data store.

Tables in Vector Store: 
```
Facts:{
    fact_id: int
    text: str
    text_vector: List[float] 
}
```
2. Data Store: MongoDB
All metadata associated to a tidyworld get stored in this 
Collections in Data Store: 
```
Tidyworld:{
    tidy_world_id: int
    nodes: [
        {
            node_id: Str | Temp ID for creation
            fact_ids: List[int] | list of fact_ids
            db_node_id: Optional[str] | In case already in DB, fill ID
        }
    ],
    edges: [
        {
            start_node_id:Str | Temp ID 
            end_node_id:  Str | Temp ID 
            fact_ids: List[int] | list of fact_ids
        }
    ]
    ** KVargs (creation_time, updation_time, tenant_id, ...) #Each tidyworld can have custom metadata in this impl
}

Tidyverse:{
    tidy_verse_id: int
    tidy_world_ids: List[int] | all tidy worlds making this verse
    ** KVargs
}

Suspect_duplicate: {
    node_id: 
    suspect_duplicate_node_id: 
}
```


## Retrival Process
TBC