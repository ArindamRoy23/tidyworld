from unittest.mock import MagicMock

import pytest

from tidyworld.extractor.ingest.router import IngestRouter
from tidyworld.models.chunk import DataSource, SourceType


@pytest.fixture
def sample_pdf_source():
    """Sample PDF data source."""
    return DataSource(source_id="test_pdf_001", source_type=SourceType.PDF, uri="local/path/to/fake.pdf")


@pytest.fixture
def default_router():
    """IngestRouter with the default PDF adapter registry."""
    return IngestRouter()


def make_docling_element(text, page_number=1, heading=None):
    """Build a mock Docling document element."""
    element = MagicMock()
    element.text = text
    element.page_number = page_number
    element.heading = heading
    return element


def make_docling_result(elements):
    """Build a mock Docling conversion result."""
    document = MagicMock()
    document.elements = elements
    result = MagicMock()
    result.document = document
    return result
