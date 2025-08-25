from dataclasses import dataclass
from abc import ABC, abstractmethod
@dataclass
class StorageNameSpace(ABC):
    pass

@dataclass
class BaseDataStore:
    pass

@dataclass
class BaseKnowledgeGraph:
    pass

@dataclass
class BaseSchema:
    pass