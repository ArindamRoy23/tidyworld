from abc import ABC, abstractmethod
from typing import List

from tidyworld.models.chunk import Chunk, ExtractionContext
from tidyworld.models.graph import GraphOutput


class ExtractionAdapter(ABC):
    """Base class for extraction."""

    @abstractmethod
    def extract(self, chunks: List[Chunk], context: ExtractionContext) -> GraphOutput:
        """Given chunks from a document, extract nodes and edges.

        ExtractionContext carries tenant_id, existing node index hints, and config.
        """
        pass
