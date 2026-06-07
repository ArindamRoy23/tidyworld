from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class SourceType(str, Enum):
    """Supported data source types across the TidyWorld ingestion pipeline."""

    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    WEB = "web"


class Tenant(str, Enum):
    """Supported tenants across the TidyWorld ingestion pipeline."""

    PUBLIC = "public"
    CLIENT = "client"


class ExtractionContext:
    """Context for the extraction process."""

    tenant: Tenant
    updated_at: datetime = datetime.now()
    metadata: Dict[str, Any] = {}


@dataclass
class DataSource:
    """Represents the raw input data before it is ingested and chunked.

    Passed into the IngestAdapter.
    """

    source_id: str
    source_type: SourceType
    uri: str  # File path, network URL, or S3 bucket location
    extraction_context: ExtractionContext  # Context for the extraction process
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
