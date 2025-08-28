I am trying to redo lightrag to make an agentic self maintaining knowledge graph. Here are the changes I am planning: |
- Instead of SQL, I want to use a NoSQL DB, to make it similar to OLAP, where multiple data types can live and query together
- I want to use pydantic data validation for every node and edge. I want an agent to keep updating this schema based on what documents are encountered. This can further be connected to external data sources to complete. For ex: 
	Person
		- Name
		- Age 
		- Phone ..
	Place
		-Name 
		-Lat/Long
		-...
- I want to link each stored piece of information to the document it is referenced from. This way, we can make the document metadata quryable at the retrieval level

# TidyWorld

TidyWorld is an agentic self-maintaining knowledge graph system designed to intelligently organize, validate, and link information from various documents and data sources.

## Overview

TidyWorld reimagines document-centric knowledge management by creating a dynamic, self-evolving graph structure that maintains data integrity while preserving source context. The system employs NoSQL database architecture for flexible data storage and intelligent schema evolution.

## Steps
    Step-1: Chunking
        Chunk document and save it to a vector DB with the metadata. 
        TODO: Add contextual chunking
    
    Step-2: Extract Nodes/Edges based on schema:
        Schema_Example:  {
            Nodes: 
                {
                    Person:
                    {
                        Name: 
                        Phone: 
                        ...
                    },
                    Place:
                    {
                        Name: 
                        Lat:
                        Long:  
                        ...
                    },

                }
            Edges:
                {
                    Person-Place:
                    {
                        Name:
                        Visited_date:
                        Visit_table_UUID:  
                        ...
                    }
                }
            }
        Schema is a pydantic-type data validation. Most fields are optional, with few core fields required for creation of Node/Entity. This schema can by dynamic/add-field-only/static
            If dynamic schema, for each document, alter the global schema based on each document, add required schema data type and field
            Elif add-field-only: Only add  field in the schemas based on information
            Else static schema, nothing can be changed 
        
    Step-3: Break to atomic factoids:
        After extraction, break each extraction in singular factoids. For ex: 
        Node of type person was detected, so 
        {
            Person:
            {
                Name: 
                Phone: 
                ...
            }
        }
        This is converted to a list of singular factoids. This is done for ease of upload and parse into NOSQL. ***To validate if a good idea. 
        Reason for atomizing: This can maintain different information sources for the same item. For ex: Name of a node changes a 100 time, we will have history of the node changes and the details. Similarlle, Phone num changes and is conflicting between docs, we are not limited to 1 anymore.  
        TODO: Maybe only save UUID here and all the textual data in the vector table???

        
        {Node-1:[{document_id, factoid:{Name: 'XYZ'}, *Whatever other items we want to store*},
        {document_id, factoid:{Phone: '123'}, *Whatever other items we want to store*}],
        Node-2:[{document_id, factoid:{Name: 'XYZ'}, *Whatever other items we want to store*},
        {document_id, factoid:{Phone: '123'}, *Whatever other items we want to store*}],
        Edge-1:[{document_id, factoid:{Name: 'XYZ'}, *Whatever other items we want to store*},
        {document_id, factoid:{Phone: '123'}, *Whatever other items we want to store*}]}
    
    Step-4: Embed the summary and look for duplication in current DB
        TODO: Validate if all this can be done agentically for google ADK 
        With the information found, look for nodes/edges already present. If no item found but suspect duplicate, Mark a suspect duplicate and create the new graph item
        In case an old graph item is added to, check for suspect duplicate and deduplicate if valid. Unlist the suspect duplicate. 
        Example NOSQL collection item: 
        {
            graph_id:UUID 
            facts: [List of factoids]
            suspect_duplicate: [List UUID] # NEED A WAY TO UPDATE THE ORIGNAL collection item
        }
    Step-5: Custom business agentic logic: 
        Any business logic goes here I guess: 
        Ex: Only nodes that exist in SQL table should exist in the graph/ 
        Get lat long for the place/ etc

Open questions: 
- How will doc level metadata be managed? 
- What will be the folder structure? 
- This is the agentic graph builder, How will we extend a retriever? What is a good design pattern for this? 


## Implementation Details

Design the project similar to fast_graphrag. 

Add the following subdirectories maybe. Just a suggestion, think carefully!!!: 
- Agents: Destination for all agents that you might want to use 
- Schema: Pick schema from here. N/E ----- *** Need to find a way to signify identifier columns!!!
- KG_Impl: Compatible KG implementation (Neo4j, Apache AGE ...) {Similar to lightRAG}
- Datastore: Data store implementation such as KV store, MongoDB.. {Similar to lightRAG}

Extractor service will look like this perhaps: 
S1. Agentic Schema create/update: Each schema will have a node/entity and its field type and a detail on what it is meant to store. Maybe add this to a vector DB ??? Also need to add identifier in  the schema (name of person/ email of user.. )

S2. Agentic extract node/entity based on the schema for each chunk. Need to figure how to do this, but it essentially is structured output. 

S3. Figure out deduplication. Differentiate node creation and node updation, two different agentic paths maybe??



Where does it differentiate from fast Graph Rag: 
    - While extracting node/edge, use an agentic extractor instead of premade queries. In someways, make it similar to the chunking, where there is a default chunker and give user power to change it. 
    - Storing factoids in NoSQL... ----- *** Need to figure this out, how to coordinate between the KG and the NoSQL 
    - Deduplication -- Change deduplication. Maybe make it agentic too 
    - After creation of node edge, give usr power to add business logic thru agents as described above. So for seperate node/edge type, have access to separate agents?? 
    - Way to ensure sync between KG and NoSQL ???    


    
    
    


    


    