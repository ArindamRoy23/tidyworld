from typing import Any, Dict

from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import ToolContext

from tidyworld._llm._default import DefaultLLMService

# Initialize LLM
llm_service = DefaultLLMService(model="groq/qwen/qwen3-32b")
llm = llm_service.get_model()

# State keys
STATE_CURRENT_GRAPH = "current_graph"
STATE_DOCUMENT = "document"
STATE_ENTITY_TYPES = "entity_types"
STATE_MISSED_ENTITIES = "missed_entities"
STATE_MISSED_RELATIONSHIPS = "missed_relationships"


# Tool to check if extraction is complete
def check_extraction_complete(tool_context: ToolContext) -> Dict[str, Any]:
    """Check if entity extraction is complete and signal to exit loop if no more entities found."""
    missed_entities = tool_context.state.get(STATE_MISSED_ENTITIES, [])
    missed_relationships = tool_context.state.get(STATE_MISSED_RELATIONSHIPS, [])

    if not missed_entities and not missed_relationships:
        print("[Extraction Complete] No more entities or relationships to extract")
        tool_context.actions.escalate = True
        return {"status": "complete", "message": "Extraction finished"}

    return {
        "status": "continue",
        "missed_entities": len(missed_entities),
        "missed_relationships": len(missed_relationships),
    }


# Initial extraction agent
initial_extractor = LlmAgent(
    name="InitialExtractor",
    model=llm,
    instruction="""You are an expert information extraction system. Your task is to extract all entities and relationships from the given document.

Document: {document}
Allowed Entity Types: {entity_types}

Extract ALL entities mentioned in the document that belong to the provided entity types. For each entity, provide a concise description capturing its key features.

Identify ALL relationships between the extracted entities. Resolve pronouns to entity names for clarity.

Output a JSON object with:
- entities: list of objects with name, type, and desc
- relationships: list of objects with source, target, and desc
- missed_entities: list of any entities you suspect might exist but couldn't confidently extract
- missed_relationships: list of any relationships you suspect might exist but couldn't confidently extract

Ensure every identified entity is part of at least one relationship.""",
    output_key=STATE_CURRENT_GRAPH,
)

# Review agent to identify missed entities
review_agent = LlmAgent(
    name="ReviewAgent",
    model=llm,
    instruction="""You are a thorough reviewer checking for missed entities and relationships in information extraction.

Current extracted graph: {current_graph}
Original document: {document}
Entity types: {entity_types}

Review the extraction carefully and identify:
1. Any entities that should have been extracted but were missed
2. Any relationships between existing entities that were missed
3. Any implicit relationships that should be made explicit
4. Any isolated entities that need to be connected

Output a JSON object with:
- missed_entities: list of missed entity names with brief descriptions
- missed_relationships: list of missed relationships with descriptions
- confidence: high/medium/low for each missed item

Be thorough but only include items you reasonably believe should be extracted.""",
    output_key=STATE_MISSED_ENTITIES,
)

# Refinement agent to add missed information
refinement_agent = LlmAgent(
    name="RefinementAgent",
    model=llm,
    instruction="""You are an expert at refining information extraction results.

Current graph: {current_graph}
Document: {document}
Entity types: {entity_types}
Missed entities: {missed_entities}
Missed relationships: {missed_relationships}

Add the missed entities and relationships to the current graph while maintaining consistency.
Ensure all entities are properly connected with relationships.

Output the complete updated graph as a JSON object with:
- entities: complete list of all entities
- relationships: complete list of all relationships
- added_entities: count of new entities added
- added_relationships: count of new relationships added

Ensure the output is valid JSON and maintains the structure of the TGraph type.""",
    output_key=STATE_CURRENT_GRAPH,
)

# Create the loop agent for iterative extraction
extraction_loop = LoopAgent(
    name="EntityExtractionLoop",
    sub_agents=[
        review_agent,  # Review current extraction
        refinement_agent,  # Add missed entities/relationships
    ],
    max_iterations=5,  # Limit iterations to prevent infinite loops
    description="Iteratively extracts entities and relationships from documents, checking for missed information",
)

# Root agent that orchestrates the extraction process
root_agent = LlmAgent(
    name="EntityExtractor",
    model=llm,
    instruction="""You are a comprehensive entity and relationship extraction system.

Given a document and entity types, perform complete information extraction including:
1. Initial extraction of all entities and relationships
2. Iterative refinement to catch missed information
3. Final validation and completeness check

Document: {document}
Entity types: {entity_types}

Use the extraction loop to ensure thoroughness. The process should continue until no more entities or relationships can be reasonably extracted.

Return the final complete graph as a properly formatted JSON object.""",
    tools=[check_extraction_complete],
)

# Export the configured agents
__all__ = ["root_agent", "extraction_loop", "initial_extractor", "review_agent", "refinement_agent"]
