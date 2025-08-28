from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union, final

from tidyworld._llm._base import BaseLLMService
from tidyworld._services._base import BaseChunkingService


@final
@dataclass
class BaseTidyWorld:
    """A class representing a template tidy world: A KG+NOSQLDB+VectorDB information store."""
    llm_service: BaseLLMService = field(init=False, default_factory=lambda: BaseLLMService(model=""))
    chunking_service: BaseChunkingService = field(default_factory=lambda: BaseChunkingService())

    # TODO: BaseInformationExtractionService(AgenticExtractor)
    information_extraction_service: BaseInformationExtractionService = field(default_factory=lambda: BaseInformationExtractionService())
    
            # Step 1: State manager insert start
        # Step 2: Chunk docs  
        # Step 3: Information extraction - Agentic??
        # Step 4: Deduplication - Agentic?
        # Step 5: Business logic - Agentic?
        # Step 6: Upsert to KG/NoSQLDB/VectorDB
        # Step 7: State manager insert end
        # Step 8: Return the result

        ## Maybe S5-S6 swap??
    state_manager: BaseStateManagerService[GTNode, GTEdge, GTHash, GTChunk, GTId, GTEmbedding] = field(
        init=False,
        default_factory=lambda: BaseStateManagerService(
            workspace=None,
            graph_storage=BaseGraphStorage[GTNode, GTEdge, GTId](config=None),
            entity_storage=BaseVectorStorage[GTId, GTEmbedding](config=None),
            chunk_storage=BaseIndexedKeyValueStorage[GTHash, GTChunk](config=None),
            embedding_service=BaseEmbeddingService(),
            node_upsert_policy=BaseNodeUpsertPolicy(config=None),
            edge_upsert_policy=BaseEdgeUpsertPolicy(config=None),
        ),
    )

    def insert(
        self,
        content: Union[str, List[str]],
        metadata: Union[List[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]] = None,
        params: Optional[InsertParam] = None,
        show_progress: bool = True
    ) -> Tuple[int, int, int]:
        return get_event_loop().run_until_complete(self.async_insert(content, metadata, params, show_progress))

    async def async_insert(
        self,
        content: Union[str, List[str]],
        metadata: Union[List[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]] = None,
        params: Optional[InsertParam] = None,
        show_progress: bool = True
    ) -> Tuple[int, int, int]:

        return (0,0,0) #TODO: Return the result, remove this later


    def query(
        self,
        query: str,
        params: Optional[QueryParam] = None,
        show_progress: bool = True
    ) -> List[str]:
        return get_event_loop().run_until_complete(self.async_query(query, params, show_progress))
