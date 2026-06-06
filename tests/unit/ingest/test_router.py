from unittest.mock import MagicMock

import pytest

from tidyworld.extractor.ingest.router import IngestRouter
from tidyworld.models.chunk import Chunk, ChunkMetadata, DataSource, SourceType


def test_router_delegates_to_pdf_adapter(sample_pdf_source):
    """Router should dispatch PDF sources to the PDF adapter."""
    mock_adapter = MagicMock()
    mock_adapter.ingest.return_value = [
        Chunk(
            text="chunk",
            metadata=ChunkMetadata(source_id=sample_pdf_source.source_id, chunk_index=0),
        )
    ]

    router = IngestRouter(adapters={SourceType.PDF: mock_adapter})
    chunks = router.ingest(sample_pdf_source)

    mock_adapter.ingest.assert_called_once_with(sample_pdf_source)
    assert len(chunks) == 1
    assert chunks[0].text == "chunk"


def test_router_raises_not_implemented_for_missing_adapter():
    """Router should raise NotImplementedError when no adapter exists for the source type."""
    router = IngestRouter()
    source = DataSource(source_id="csv_001", source_type=SourceType.CSV, uri="data.csv")

    with pytest.raises(NotImplementedError, match="No ingest adapter implemented for source type: csv"):
        router.ingest(source)


def test_router_register_adds_new_adapter():
    """Router should support registering adapters for additional source types."""
    mock_adapter = MagicMock()
    mock_adapter.ingest.return_value = []

    router = IngestRouter()
    source = DataSource(source_id="csv_001", source_type=SourceType.CSV, uri="data.csv")

    router.register(SourceType.CSV, mock_adapter)
    router.ingest(source)

    mock_adapter.ingest.assert_called_once_with(source)
