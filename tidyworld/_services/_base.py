import asyncio
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel

from tidyworld._llm._base import BaseLLMService
from tidyworld._models import BaseModelAlias
from tidyworld._types import GTChunk, GTEdge, GTId, GTNode, TDocument

T_model = TypeVar("T_model", bound=Union[BaseModel, BaseModelAlias])
TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


@dataclass
class BaseChunkingService(Generic[GTChunk]):
  """Base class for chunk extractor."""

  def __post__init__(self):
    pass

  async def extract(self, data: Iterable[TDocument]) -> Iterable[Iterable[GTChunk]]:
    """Extract unique chunks from the given data."""
    raise NotImplementedError


@dataclass
class BaseInformationExtractionService(Generic[GTChunk, GTNode, GTEdge, GTId]):
  """Base class for entity and relationship extractors."""

  graph_upsert: BaseGraphUpsertPolicy[GTNode, GTEdge, GTId]
  max_gleaning_steps: int = 0

  def extract(
    self,
    llm: BaseLLMService,
    documents: Iterable[Iterable[GTChunk]],
    prompt_kwargs: Dict[str, str],
    entity_types: List[str],
  ) -> List[asyncio.Future[Optional[BaseGraphStorage[GTNode, GTEdge, GTId]]]]:
    """Extract both entities and relationships from the given data."""
    raise NotImplementedError

  async def extract_entities_from_query(
    self, llm: BaseLLMService, query: str, prompt_kwargs: Dict[str, str]
  ) -> Dict[str, List[str]]:
    """Extract entities from the given query."""
    raise NotImplementedError
