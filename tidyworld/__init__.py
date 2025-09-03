from dataclasses import dataclass, field
from typing import Type

from tidyworld._llm import (
  BaseEmbeddingService,
  BaseLLMService,
  DefaultEmbeddingService,
  DefaultLLMService,
  LiteLLMEmbeddingService,
  LiteLLMService,
)
from tidyworld._services import (
  BaseChunkingService,
  BaseDataModelService,
  BaseInformationExtractionService,
  DefaultChunkingService,
  DefaultDataModelService,
  DefaultInformationExtractionService,
)
from tidyworld._storage import (
  BaseGraphStorage,
  BaseIndexedKeyValueStorage,
  BaseVectorStorage,
  DefaultGraphStorage,
  DefaultGraphStorageConfig,
  DefaultIndexedKeyValueStorage,
  DefaultVectorStorage,
  DefaultVectorStorageConfig,
)
from tidyworld._tidyworld import BaseTidyWorld
from tidyworld._types import (
  GTChunk,
  GTEdge,
  GTEmbedding,
  GTHash,
  GTId,
  GTNode,
  TChunk,
  TEmbedding,
  TEntity,
  THash,
  TId,
  TIndex,
  TRelation,
)


@dataclass
class TidyWorld(BaseTidyWorld[GTEmbedding, GTHash, GTChunk, GTNode, GTEdge, GTId]):
  """TidyWorld class."""

  @dataclass
  class Config:
    """Configuration for the TidyWorld class."""

    chunking_service_cls: Type[BaseChunkingService[TChunk]] = field(default=DefaultChunkingService)
    data_model_service_cls: Type[BaseDataModelService] = field(default=DefaultDataModelService)
    llm_service: BaseLLMService = field(default_factory=lambda: DefaultLLMService())
    embedding_service: BaseEmbeddingService = field(default_factory=lambda: DefaultEmbeddingService())
    information_extraction_service_cls: Type[BaseInformationExtractionService] = field(
      default=DefaultInformationExtractionService
    )

    graph_storage: BaseGraphStorage[TEntity, TRelation, TId] = field(
      default_factory=lambda: DefaultGraphStorage(DefaultGraphStorageConfig(node_cls=TEntity, edge_cls=TRelation))
    )
    vector_storage: DefaultVectorStorage[TIndex, TEmbedding] = field(
      default_factory=lambda: DefaultVectorStorage(DefaultVectorStorageConfig())
    )
    chunk_storage: DefaultIndexedKeyValueStorage[THash, TChunk] = field(
      default_factory=lambda: DefaultIndexedKeyValueStorage(None)
    )

    def __post_init__(self):
      """Initialize the GraphRAG Config class."""
      pass

  config: Config = field(default_factory=Config)

  def __post_init__(self):
    """Initialize the GraphRAG class."""
    self.llm_service = self.config.llm_service
    self.embedding_service = self.config.embedding_service
    self.chunking_service = self.config.chunking_service_cls()
    # self.information_extraction_service = self.config.information_extraction_service_cls(
    #   graph_upsert=self.config.information_extraction_upsert_policy
    # )
    # self.state_manager = self.config.state_manager_cls(
    #     workspace=Workspace.new(self.working_dir, keep_n=self.n_checkpoints),
    #     embedding_service=self.embedding_service,
    #     graph_storage=self.config.graph_storage,
    #     entity_storage=self.config.entity_storage,
    #     chunk_storage=self.config.chunk_storage,
    #     entity_ranking_policy=self.config.entity_ranking_policy,
    #     relation_ranking_policy=self.config.relation_ranking_policy,
    #     chunk_ranking_policy=self.config.chunk_ranking_policy,
    #     node_upsert_policy=self.config.node_upsert_policy,
    #     edge_upsert_policy=self.config.edge_upsert_policy,
    # )
