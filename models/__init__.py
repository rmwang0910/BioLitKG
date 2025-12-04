"""数据模型"""
from .relations import (
    RelationType, EntityType, Entity, Relation,
    PaperNode, KnowledgeGraphSummary
)
from .graph import KnowledgeGraph

__all__ = [
    'RelationType', 'EntityType', 'Entity', 'Relation',
    'PaperNode', 'KnowledgeGraphSummary', 'KnowledgeGraph'
]
