from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


@dataclass
class SourceType(str, Enum):
    """Supported data source types across the TidyWorld ingestion pipeline."""

    PDF = "pdf"


@dataclass
class DataSource:
    """Represents the raw input data before it is ingested and chunked.

    Passed into the IngestAdapter.
    """

    source_id: str
    source_type: str  # e.g., "pdf", "csv", "url", "json"
    uri: str  # File path, network URL, or S3 bucket location
    metadata: Dict[str, Any] = field(default_factory=dict)
    raw_content: Optional[bytes] = None  # Optional: for holding file bytes directly in memory


@dataclass
class ChunkMetadata:
    """Metadata carrying the origin details of the chunk."""

    source_id: str  # Foreign key linking back to the DataSource
    chunk_index: int
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    char_offset: Optional[int] = None


@dataclass
class Chunk:
    """The fundamental unit of text ingested from a data source."""

    text: str
    metadata: ChunkMetadata
