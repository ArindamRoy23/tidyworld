from dataclasses import dataclass
from base import BaseDataStore, BaseKnowledgeGraph, BaseSchema
from typing import final

@final
@dataclass
class TidyWorld:
    def __init__(self,
        data_store: BaseDataStore,
        knowledge_graph: BaseKnowledgeGraph,
        schema: BaseSchema,
    ) -> None:
    # TODO: Add docstring
        '''
        []
        '''
        self.data_store = data_store
        self.knowledge_graph = knowledge_graph
        self.schema = schema
    def __post_init__(self) -> None:
        # Initialize all possible components
        pass
    
    def insert(self):
        pass

    def query(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass