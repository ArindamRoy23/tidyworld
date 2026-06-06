from typing import Dict, List, Optional

from tidyworld.extractor.ingest.base import IngestAdapter
from tidyworld.extractor.ingest.pdf import PdfIngestAdapter
from tidyworld.models.chunk import Chunk, DataSource, SourceType


class IngestRouter:
    """Routes a DataSource to the appropriate IngestAdapter based on source_type."""

    def __init__(self, adapters: Optional[Dict[SourceType, IngestAdapter]] = None):
        """Initialise the router with optional custom adapter registry."""
        if adapters is None:
            self._adapters = {SourceType.PDF: PdfIngestAdapter()}
        else:
            self._adapters = adapters

    def ingest(self, source: DataSource) -> List[Chunk]:
        """Route the source to its adapter and return chunks."""
        if source.source_type not in self._adapters:
            raise NotImplementedError(
                f"No ingest adapter implemented for source type: {source.source_type.value}"
            )
        return self._adapters[source.source_type].ingest(source)

    def register(self, source_type: SourceType, adapter: IngestAdapter) -> None:
        """Register or replace an adapter for a source type."""
        self._adapters[source_type] = adapter
