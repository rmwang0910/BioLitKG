"""
关系类型定义和数据模型
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RelationType(str, Enum):
    """文献关系类型"""
    # 引用关系
    CITES = "cites"  # A引用B
    CITED_BY = "cited_by"  # A被B引用
    
    # 概念关系
    SIMILAR_TOPIC = "similar_topic"  # 相似主题
    EXTENDS = "extends"  # 扩展/改进
    CONTRADICTS = "contradicts"  # 矛盾/反驳
    SUPPORTS = "supports"  # 支持
    
    # 方法关系
    USES_METHOD = "uses_method"  # 使用方法
    IMPROVES_METHOD = "improves_method"  # 改进方法
    COMPARES_WITH = "compares_with"  # 比较
    
    # 实体关系
    STUDIES_ENTITY = "studies_entity"  # 研究某个实体(基因、蛋白质等)
    RELATED_ENTITY = "related_entity"  # 相关实体
    
    # 其他
    SAME_AUTHOR = "same_author"  # 同一作者
    SAME_FIELD = "same_field"  # 同一领域


class EntityType(str, Enum):
    """实体类型"""
    GENE = "gene"
    PROTEIN = "protein"
    DISEASE = "disease"
    DRUG = "drug"
    PATHWAY = "pathway"
    CELL_TYPE = "cell_type"
    TISSUE = "tissue"
    ORGANISM = "organism"
    METHOD = "method"
    CONCEPT = "concept"
    DATASET = "dataset"


class Entity(BaseModel):
    """实体"""
    id: str = Field(description="实体唯一标识")
    name: str = Field(description="实体名称")
    type: EntityType = Field(description="实体类型")
    aliases: List[str] = Field(default_factory=list, description="别名")
    properties: Dict[str, Any] = Field(default_factory=dict, description="额外属性")
    
    def __hash__(self):
        return hash(self.id)


class Relation(BaseModel):
    """文献或实体间的关系"""
    id: str = Field(description="关系唯一标识")
    source_id: str = Field(description="源节点ID")
    target_id: str = Field(description="目标节点ID")
    relation_type: RelationType = Field(description="关系类型")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度")
    evidence: Optional[str] = Field(default=None, description="证据文本")
    properties: Dict[str, Any] = Field(default_factory=dict, description="额外属性")
    created_at: datetime = Field(default_factory=datetime.now)
    
    def __hash__(self):
        return hash(self.id)


class PaperNode(BaseModel):
    """论文节点"""
    id: str = Field(description="论文ID (DOI/arXiv/PubMed)")
    title: str = Field(description="标题")
    authors: List[str] = Field(default_factory=list, description="作者列表")
    year: Optional[int] = Field(default=None, description="发表年份")
    abstract: str = Field(default="", description="摘要")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    fields: List[str] = Field(default_factory=list, description="研究领域")
    citation_count: int = Field(default=0, description="引用数")
    url: Optional[str] = Field(default=None, description="URL")
    
    # 提取的实体
    entities: List[Entity] = Field(default_factory=list, description="提取的实体")
    
    # 元数据
    source: str = Field(default="unknown", description="数据源")
    properties: Dict[str, Any] = Field(default_factory=dict, description="额外属性")
    
    def __hash__(self):
        return hash(self.id)


class KnowledgeGraphSummary(BaseModel):
    """知识图谱摘要统计"""
    num_papers: int = Field(description="论文数量")
    num_entities: int = Field(description="实体数量")
    num_relations: int = Field(description="关系数量")
    relation_type_distribution: Dict[str, int] = Field(description="关系类型分布")
    entity_type_distribution: Dict[str, int] = Field(description="实体类型分布")
    top_papers: List[Dict[str, Any]] = Field(description="高引论文")
    top_entities: List[Dict[str, Any]] = Field(description="高频实体")
    time_range: Optional[Dict[str, int]] = Field(default=None, description="时间范围")

