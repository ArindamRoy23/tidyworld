import asyncio
import re
from dataclasses import dataclass
from typing import Generic, Iterable, List, Optional, TypeVar, Union

from pydantic import BaseModel

from tidyworld._models import BaseModelAlias
from tidyworld._storage import BaseGraphStorage
from tidyworld._types import GTChunk, GTEdge, GTId, GTNode, TDocument, TSchemaDefinition

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


class BaseDataModelService:
  """Base class for schema management."""

  def __post__init__(self):
    pass

  async def read_schema(self, source: TSchemaDefinition):
    """Read the schema from some source."""
    raise NotImplementedError

  async def create_node_data_model(self, data):
    """Create a node schema from the given data."""
    raise NotImplementedError

  async def create_edge_data_model(self, data):
    """Create an edge schema from the given data."""
    raise NotImplementedError

  async def update_node_data_model(self, data):
    """Update a node schema from the given data."""
    raise NotImplementedError

  async def update_edge_data_model(self, data):
    """Update an edge schema from the given data."""
    raise NotImplementedError

  async def delete_node_data_model(self, data):
    """Delete a node schema from the given data."""
    raise NotImplementedError

  async def delete_edge_data_model(self, data):
    """Delete an edge schema from the given data."""
    raise NotImplementedError


class BaseInformationExtractionService:
  """Base class for information extraction."""

  async def extract(self, data) -> List[asyncio.Future[Optional[BaseGraphStorage[GTNode, GTEdge, GTId]]]]:
    """Extract information from the given data."""
    raise NotImplementedError
