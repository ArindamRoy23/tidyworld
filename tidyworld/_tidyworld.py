from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Tuple, Union

from tidyworld._llm._base import BaseEmbeddingService, BaseLLMService
from tidyworld._services._base import BaseChunkingService, BaseDataModelService, BaseInformationExtractionService

# from tidyworld._services._state_manager import BaseStateManagerService
from tidyworld._types import GTChunk, GTEdge, GTEmbedding, GTHash, GTId, GTNode, TDocument
from tidyworld._utils import get_event_loop, logger


@dataclass
class InsertParam:
    pass


@dataclass
class BaseTidyWorld(Generic[GTEmbedding, GTHash, GTChunk, GTNode, GTEdge, GTId]):
    """A class representing a template tidy world: A KG+NOSQLDB+VectorDB information store."""

    data_model_service: BaseDataModelService = field(
        default_factory=lambda: BaseDataModelService()
    )  # TODO: To be created
    # TODO: maybe not needed
    llm_service: BaseLLMService = field(init=False, default_factory=lambda: BaseLLMService(model=""))
    embedding_service: BaseEmbeddingService = field(init=False, default_factory=lambda: BaseEmbeddingService(model=""))
    chunking_service: BaseChunkingService = field(default_factory=lambda: BaseChunkingService())

    # TODO: BaseInformationExtractionService(AgenticExtractor)
    information_extraction_service: BaseInformationExtractionService = field(
        default_factory=lambda: BaseInformationExtractionService()
    )

    # Step 1: State manager insert start
    # Step 2: Chunk docs
    # Step 3: Information extraction - Agentic??
    # Step 4: Deduplication - Agentic?
    # Step 5: Business logic - Agentic?
    # Step 6: Upsert to KG/NoSQLDB/VectorDB
    # Step 7: State manager insert end
    # Step 8: Return the result

    ## Maybe S5-S6 swap??
    ## Step 3-5 is all inside ExtractionService

    #   state_manager: BaseStateManagerService[GTNode, GTEdge, GTHash, GTChunk, GTId, GTEmbedding] = field(
    #     init=False,
    #     default_factory=lambda: BaseStateManagerService(
    #       workspace=None,
    #       graph_storage=BaseGraphStorage[GTNode, GTEdge, GTId](config=None),
    #       entity_storage=BaseVectorStorage[GTId, GTEmbedding](config=None),
    #       chunk_storage=BaseIndexedKeyValueStorage[GTHash, GTChunk](config=None),
    #       embedding_service=BaseEmbeddingService(),
    #       node_upsert_policy=BaseNodeUpsertPolicy(config=None),
    #       edge_upsert_policy=BaseEdgeUpsertPolicy(config=None),
    #     ),
    #   )

    def insert(
        self,
        content: Union[str, List[str]],
        metadata: Union[List[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]] = None,
        params: Optional[InsertParam] = None,
        show_progress: bool = True,
    ) -> Tuple[int, int, int]:
        return get_event_loop().run_until_complete(self.async_insert(content, metadata, params, show_progress))

    async def async_insert(
        self,
        content: Union[str, List[str]],
        metadata: Union[List[Optional[Dict[str, Any]]], Optional[Dict[str, Any]]] = None,
        params: Optional[InsertParam] = None,
        show_progress: bool = True,
    ) -> Tuple[int, int, int]:
        """Insert a new memory or memories into the graph.

        Args:
            content (str | list[str]): The data to be inserted. Can be a single string or a list of strings.
            metadata (dict, optional): Additional metadata associated with the data. Defaults to None.
            params (InsertParam, optional): Additional parameters for the insertion. Defaults to None.
            show_progress (bool, optional): Whether to show the progress bar. Defaults to True.
        """
        if params is None:
            params = InsertParam()
        if isinstance(content, str):
            content = [content]
        if isinstance(metadata, dict):
            metadata = [metadata]
        if metadata is None or isinstance(metadata, dict):
            data = (TDocument(data=c, metadata=metadata or {}) for c in content)
        else:
            # TODO: Maybe add validation to check if content and metadata are of the same length.
            data = (TDocument(data=c, metadata=m or {}) for c, m in zip(content, metadata))

        try:
            """Pseudocode:
      Step 0: Store the raw documents in the nosql. (Do this as part of insert_start)
      Step 1: State manager insert start. TODO: Decide what all will be done in this step.
      Step 2: Chunk docs
      Step 3: Call an agentic pipeline to extract entities and relationships. Create a default for this.
      Step 6: Upsert to KG/NoSQLDB/VectorDB using hybrid storage manager. TODO: Decide if service or storage manager.
      Step 7: State manager insert end. TODO: Decide what all will be done in this step.
      Step 8: Return the result
      """
            # await self.state_manager.insert_start()
            chunked_documents = await self.chunking_service.extract(data=data)
            # TODO: Store the chunked documents in the vdb.

            await self.information_extraction_service.extract(data=chunked_documents)
            # self.state_manager.insert_end()

            pass
        except Exception as e:
            logger.error(f"Error during insertion: {e}")
            raise e
        return (0, 0, 0)  # TODO: Return the result, remove this later

    # TODO: Implement query function
    # def query(
    #     self,
    #     query: str,
    #     params: Optional[QueryParam] = None,
    #     show_progress: bool = True
    # ) -> List[str]:
    #     return get_event_loop().run_until_complete(self.async_query(query, params, show_progress))
