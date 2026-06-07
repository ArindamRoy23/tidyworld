from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    """A node in the graph."""
    node_id: str
    facts: List[str]
    db_node_id: Optional[str] = None

@dataclass
class Edge:
    """An edge in the graph."""

    start_node_id: str
    end_node_id: str
    facts: List[str]
    predicate: Optional[str] = None

@dataclass
class GraphOutput:
    """Output of the extraction process."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
