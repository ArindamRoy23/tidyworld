from unittest.mock import MagicMock, patch

import pytest

from tidyworld.extractor.ingest.pdf import PdfIngestAdapter
from tidyworld.models.chunk import DataSource, SourceType


def test_pdf_adapter_rejects_non_pdf():
    """Ensure the adapter violently fails if routed the wrong file type."""
    adapter = PdfIngestAdapter()
    bad_source = DataSource(source_id="bad_001", source_type=SourceType.CSV, uri="test.csv")

    with pytest.raises(ValueError, match="expects PDF"):
        adapter.ingest(bad_source)


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_pdf_adapter_extracts_chunks(mock_docling_converter, sample_pdf_source):
    """Ensure the adapter correctly maps Docling's data structure to TidyWorld Chunks."""
    mock_instance = mock_docling_converter.return_value

    el_1 = MagicMock()
    el_1.text = "TidyWorld is a scalable graph."
    el_1.page_number = 1
    el_1.heading = "1. Overview"

    el_2 = MagicMock()
    el_2.text = "Empty texts should be ignored."
    el_2.page_number = 2
    el_2.heading = "2. Terminology"

    el_empty = MagicMock()
    el_empty.text = "   "  # Whitespace should be skipped by the adapter

    # Attach elements to the mock document
    mock_doc = MagicMock()
    mock_doc.elements = [el_1, el_empty, el_2]

    # Make the convert() method return our fake document
    mock_result = MagicMock()
    mock_result.document = mock_doc
    mock_instance.convert.return_value = mock_result

    # 2. Execute the Code Under Test
    adapter = PdfIngestAdapter()
    chunks = adapter.ingest(sample_pdf_source)

    # 3. Assertions
    # We passed 3 elements, but 1 was whitespace, so we expect 2 chunks
    assert len(chunks) == 2

    # Verify the text was captured
    assert chunks[0].text == "TidyWorld is a scalable graph."
    assert chunks[1].text == "Empty texts should be ignored."

    # Verify the ChunkMetadata was mapped correctly
    assert chunks[0].metadata.source_id == sample_pdf_source.source_id
    assert chunks[0].metadata.chunk_index == 0
    assert chunks[0].metadata.page_number == 1
    assert chunks[0].metadata.section_heading == "1. Overview"

    # Verify the index increments correctly despite the skipped empty element
    assert chunks[1].metadata.chunk_index == 2
    assert chunks[1].metadata.page_number == 2

    # Verify that the converter was actually called with the correct URI
    mock_instance.convert.assert_called_once_with(sample_pdf_source.uri)
