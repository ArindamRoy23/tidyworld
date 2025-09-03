import asyncio
from typing import Dict, Iterable, List, Optional

from tidyworld._llm._base import BaseLLMService
from tidyworld._services._base import BaseInformationExtractionService
from tidyworld._storage import BaseGraphStorage
from tidyworld._types import GTId, TChunk, TEntity, TRelation


class DefaultInformationExtractionService(BaseInformationExtractionService):
    async def extract(
        self, documents, llm_service: BaseLLMService, prompt_kwargs: Dict[str, str]
    ) -> List[asyncio.Future[Optional[BaseGraphStorage[TEntity, TRelation, GTId]]]]:
        return [
            asyncio.create_task(self.extract_unique_async(llm_service, document, prompt_kwargs))
            for document in documents
        ]

    async def extract_unique_async(
        self,
        llm_service: BaseLLMService,
        chunks: Iterable[TChunk],
        prompt_kwargs: Dict[str, str],
    ) -> Optional[BaseGraphStorage[TEntity, TRelation, GTId]]:
        """This is the main function that will be used to extract information from the documents.

        Psudocode:
        1. Extract in Loop using google ADK with gleaning.
        2. For each node, verify node schema. [Exists, Add, or Create New]
        3. For each edge, verify edge schema. [Exists, Add, or Create New]
        """
        pass
