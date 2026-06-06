from typing import List

from docling.document_converter import DocumentConverter

from tidyworld.extractor.ingest.base import IngestAdapter
from tidyworld.models.chunk import Chunk, ChunkMetadata, DataSource, SourceType


class PdfIngestAdapter(IngestAdapter):
    """Ingests PDF documents using Docling for structural extraction."""

    def __init__(self):
        """Init class."""
        self.converter = DocumentConverter()

    def ingest(self, source: DataSource) -> List[Chunk]:
        """Ingest PDFs."""
        if source.source_type != SourceType.PDF:
            raise ValueError(f"PdfIngestAdapter expects PDF, got {source.source_type}")

        chunks: List[Chunk] = []
        result = self.converter.convert(source.uri)
        doc = result.document

        for i, element in enumerate(doc.elements):
            text = element.text
            if not text or not text.strip():
                continue

            metadata = ChunkMetadata(
                source_id=source.source_id,
                chunk_index=i,
                page_number=element.page_number,
                section_heading=self._get_heading_context(element),  # Custom helper
                char_offset=None,
            )

            chunks.append(Chunk(text=text, metadata=metadata))

        return self._apply_semantic_chunking(chunks)

    def _get_heading_context(self, element) -> str | None:
        """Helper to extract the nearest heading for context."""
        # Implementation depends on Docling's specific element hierarchy API
        return getattr(element, "heading", None)

    def _apply_semantic_chunking(self, chunks: List[Chunk]) -> List[Chunk]:
        """Optional: Combine or split chunks to fit token limits.

        When passing data downstream to NLP extraction agents, respecting
        token limits and maintaining semantic boundaries is critical to
        preventing context loss.
        """
        return chunks
