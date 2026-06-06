from unittest.mock import MagicMock

import pytest

from tidyworld.extractor.ingest.router import IngestRouter
from tidyworld.models.chunk import DataSource, SourceType


@pytest.mark.parametrize(
    "source_type,uri",
    [
        (SourceType.CSV, "data.csv"),
        (SourceType.JSON, "data.json"),
        (SourceType.WEB, "https://example.com"),
    ],
)
def test_router_raises_not_implemented_for_unregistered_types(source_type, uri):
    """Default router should reject source types with no registered adapter."""
    router = IngestRouter()
    source = DataSource(source_id="unregistered_001", source_type=source_type, uri=uri)

    with pytest.raises(NotImplementedError, match=f"source type: {source_type.value}"):
        router.ingest(source)


def test_router_raises_not_implemented_when_registry_is_empty(sample_pdf_source):
    """An explicitly empty registry should fail even for PDF."""
    router = IngestRouter(adapters={})

    with pytest.raises(NotImplementedError, match="source type: pdf"):
        router.ingest(sample_pdf_source)


def test_router_propagates_adapter_errors(sample_pdf_source):
    """Adapter exceptions should not be swallowed by the router."""
    failing_adapter = MagicMock()
    failing_adapter.ingest.side_effect = ValueError("adapter failed")

    router = IngestRouter(adapters={SourceType.PDF: failing_adapter})

    with pytest.raises(ValueError, match="adapter failed"):
        router.ingest(sample_pdf_source)


def test_router_register_replaces_existing_adapter(sample_pdf_source):
    """Registering a second adapter for the same type should replace the first."""
    first_adapter = MagicMock()
    first_adapter.ingest.return_value = []
    second_adapter = MagicMock()
    second_adapter.ingest.return_value = []

    router = IngestRouter(adapters={SourceType.PDF: first_adapter})
    router.register(SourceType.PDF, second_adapter)
    router.ingest(sample_pdf_source)

    first_adapter.ingest.assert_not_called()
    second_adapter.ingest.assert_called_once_with(sample_pdf_source)
