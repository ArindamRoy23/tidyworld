from unittest.mock import patch

import pytest

from tests.conftest import make_docling_element, make_docling_result
from tidyworld.extractor.ingest.pdf import PdfIngestAdapter
from tidyworld.extractor.ingest.router import IngestRouter
from tidyworld.models.chunk import DataSource, SourceType


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_router_routes_pdf_through_default_adapter(mock_docling_converter, sample_pdf_source):
    """Default router should wire PDF sources to PdfIngestAdapter without mocks."""
    mock_docling_converter.return_value.convert.return_value = make_docling_result(
        [
            make_docling_element("First paragraph.", page_number=1, heading="Intro"),
            make_docling_element("Second paragraph.", page_number=2, heading="Details"),
        ]
    )

    router = IngestRouter()
    chunks = router.ingest(sample_pdf_source)

    assert len(chunks) == 2
    assert chunks[0].text == "First paragraph."
    assert chunks[1].text == "Second paragraph."
    mock_docling_converter.return_value.convert.assert_called_once_with(sample_pdf_source.uri)


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_router_pdf_integration_preserves_source_metadata(mock_docling_converter):
    """Source identity should flow from DataSource through router into chunk metadata."""
    source = DataSource(
        source_id="integration_pdf_42",
        source_type=SourceType.PDF,
        uri="/tmp/integration.pdf",
        tenant="tenant-a",
    )
    mock_docling_converter.return_value.convert.return_value = make_docling_result(
        [make_docling_element("Tenant-scoped content.", page_number=3, heading="Scope")]
    )

    router = IngestRouter()
    chunks = router.ingest(source)

    assert len(chunks) == 1
    assert chunks[0].metadata.source_id == "integration_pdf_42"
    assert chunks[0].metadata.chunk_index == 0
    assert chunks[0].metadata.page_number == 3
    assert chunks[0].metadata.section_heading == "Scope"


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_router_pdf_integration_skips_blank_elements(mock_docling_converter, sample_pdf_source):
    """Router + PDF adapter should skip blank elements as a single pipeline."""
    mock_docling_converter.return_value.convert.return_value = make_docling_result(
        [
            make_docling_element("Keep me."),
            make_docling_element("   "),
            make_docling_element("Keep me too."),
        ]
    )

    router = IngestRouter()
    chunks = router.ingest(sample_pdf_source)

    assert len(chunks) == 2
    assert [chunk.text for chunk in chunks] == ["Keep me.", "Keep me too."]
    assert chunks[1].metadata.chunk_index == 2


def test_router_default_registry_uses_pdf_adapter_instance(default_router):
    """Default router should register a real PdfIngestAdapter instance."""
    adapter = default_router._adapters[SourceType.PDF]

    assert isinstance(adapter, PdfIngestAdapter)


def test_router_blocks_csv_before_pdf_adapter_is_invoked(default_router):
    """Unimplemented types should fail at the router without touching Docling."""
    source = DataSource(source_id="csv_001", source_type=SourceType.CSV, uri="data.csv")

    with pytest.raises(NotImplementedError, match="source type: csv"):
        default_router.ingest(source)
