from abc import ABC, abstractmethod
from typing import List

from tidyworld.models.chunk import Chunk, DataSource


class IngestAdapter(ABC):
    """Base class for ingestion."""
    @abstractmethod
    def ingest(self, source: DataSource) -> List[Chunk]:
        """Accept a raw data source and return an ordered list of text chunks.

        Each chunk carries metadata about its origin (page, section, offset, etc.)
        """
        pass
