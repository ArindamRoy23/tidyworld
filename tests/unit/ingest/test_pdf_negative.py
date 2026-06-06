from unittest.mock import MagicMock, patch

import pytest

from tidyworld.extractor.ingest.pdf import PdfIngestAdapter
from tidyworld.models.chunk import DataSource, SourceType


@pytest.mark.parametrize(
    "source_type",
    [SourceType.CSV, SourceType.JSON, SourceType.WEB],
)
def test_pdf_adapter_rejects_non_pdf_source_types(source_type):
    """PdfIngestAdapter must reject any source that is not PDF."""
    adapter = PdfIngestAdapter()
    source = DataSource(source_id="bad_001", source_type=source_type, uri="data/file")

    with pytest.raises(ValueError, match="expects PDF"):
        adapter.ingest(source)


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_pdf_adapter_propagates_converter_errors(mock_docling_converter, sample_pdf_source):
    """Docling conversion failures should bubble up unchanged."""
    mock_docling_converter.return_value.convert.side_effect = FileNotFoundError("missing.pdf")

    adapter = PdfIngestAdapter()

    with pytest.raises(FileNotFoundError, match="missing.pdf"):
        adapter.ingest(sample_pdf_source)


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_pdf_adapter_returns_empty_list_for_empty_document(mock_docling_converter, sample_pdf_source):
    """A PDF with no elements should produce no chunks."""
    mock_result = MagicMock()
    mock_result.document = MagicMock(elements=[])
    mock_docling_converter.return_value.convert.return_value = mock_result

    chunks = PdfIngestAdapter().ingest(sample_pdf_source)

    assert chunks == []


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_pdf_adapter_returns_empty_list_when_all_elements_are_blank(mock_docling_converter, sample_pdf_source):
    """Whitespace-only elements should all be skipped."""
    blank_1 = MagicMock(text="")
    blank_2 = MagicMock(text="   \n\t  ")

    mock_result = MagicMock()
    mock_result.document = MagicMock(elements=[blank_1, blank_2])
    mock_docling_converter.return_value.convert.return_value = mock_result

    chunks = PdfIngestAdapter().ingest(sample_pdf_source)

    assert chunks == []


@patch("tidyworld.extractor.ingest.pdf.DocumentConverter")
def test_pdf_adapter_handles_missing_optional_element_metadata(mock_docling_converter, sample_pdf_source):
    """Elements without page numbers or headings should still produce valid chunks."""
    element = MagicMock()
    element.text = "Metadata-light chunk."
    element.page_number = None
    element.heading = None

    mock_result = MagicMock()
    mock_result.document = MagicMock(elements=[element])
    mock_docling_converter.return_value.convert.return_value = mock_result

    chunks = PdfIngestAdapter().ingest(sample_pdf_source)

    assert len(chunks) == 1
    assert chunks[0].text == "Metadata-light chunk."
    assert chunks[0].metadata.page_number is None
    assert chunks[0].metadata.section_heading is None
