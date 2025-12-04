"""
知识图谱数据结构
"""
import json
from typing import List, Dict, Set, Optional, Any
from collections import defaultdict
import networkx as nx
from datetime import datetime

from .relations import (
    PaperNode, Entity, Relation, EntityType, RelationType,
    KnowledgeGraphSummary
)


class KnowledgeGraph:
    """文献知识图谱"""
    
    def __init__(self):
        """初始化知识图谱"""
        self.papers: Dict[str, PaperNode] = {}
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        
        # NetworkX图用于分析
        self.graph = nx.DiGraph()
        
    def add_paper(self, paper: PaperNode):
        """添加论文节点"""
        if paper.id not in self.papers:
            self.papers[paper.id] = paper
            self.graph.add_node(
                paper.id,
                type="paper",
                title=paper.title,
                year=paper.year,
                citation_count=paper.citation_count
            )
            
    def add_entity(self, entity: Entity):
        """添加实体节点"""
        if entity.id not in self.entities:
            self.entities[entity.id] = entity
            self.graph.add_node(
                entity.id,
                type="entity",
                name=entity.name,
                entity_type=entity.type.value
            )
            
    def add_relation(self, relation: Relation):
        """添加关系边"""
        self.relations.append(relation)
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            relation_type=relation.relation_type.value,
            confidence=relation.confidence,
            evidence=relation.evidence or ""
        )
        
    def get_paper_relations(self, paper_id: str) -> List[Relation]:
        """获取论文的所有关系"""
        return [
            r for r in self.relations
            if r.source_id == paper_id or r.target_id == paper_id
        ]
        
    def get_entity_papers(self, entity_id: str) -> List[PaperNode]:
        """获取提到某实体的所有论文"""
        papers = []
        for paper in self.papers.values():
            if any(e.id == entity_id for e in paper.entities):
                papers.append(paper)
        return papers
        
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """查找两个节点间的最短路径"""
        try:
            return nx.shortest_path(self.graph, source_id, target_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
            
    def get_connected_components(self) -> List[Set[str]]:
        """获取连通分量"""
        undirected = self.graph.to_undirected()
        return list(nx.connected_components(undirected))
        
    def calculate_centrality(self) -> Dict[str, float]:
        """计算节点中心性"""
        if len(self.graph.nodes()) == 0:
            return {}
        try:
            return nx.pagerank(self.graph)
        except:
            return {node: 0.0 for node in self.graph.nodes()}
            
    def get_summary(self) -> KnowledgeGraphSummary:
        """生成知识图谱摘要"""
        # 关系类型分布
        relation_dist = defaultdict(int)
        for r in self.relations:
            relation_dist[r.relation_type.value] += 1
            
        # 实体类型分布
        entity_dist = defaultdict(int)
        for e in self.entities.values():
            entity_dist[e.type.value] += 1
            
        # 高引论文 (Top 10)
        top_papers = sorted(
            [
                {
                    "id": p.id,
                    "title": p.title,
                    "citation_count": p.citation_count,
                    "year": p.year
                }
                for p in self.papers.values()
            ],
            key=lambda x: x["citation_count"],
            reverse=True
        )[:10]
        
        # 高频实体 (Top 10)
        entity_paper_count = defaultdict(int)
        for paper in self.papers.values():
            for entity in paper.entities:
                entity_paper_count[entity.id] += 1
                
        top_entities = sorted(
            [
                {
                    "id": e_id,
                    "name": self.entities[e_id].name if e_id in self.entities else e_id,
                    "type": self.entities[e_id].type.value if e_id in self.entities else "unknown",
                    "paper_count": count
                }
                for e_id, count in entity_paper_count.items()
            ],
            key=lambda x: x["paper_count"],
            reverse=True
        )[:10]
        
        # 时间范围
        years = [p.year for p in self.papers.values() if p.year]
        time_range = None
        if years:
            time_range = {"min_year": min(years), "max_year": max(years)}
            
        return KnowledgeGraphSummary(
            num_papers=len(self.papers),
            num_entities=len(self.entities),
            num_relations=len(self.relations),
            relation_type_distribution=dict(relation_dist),
            entity_type_distribution=dict(entity_dist),
            top_papers=top_papers,
            top_entities=top_entities,
            time_range=time_range
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "papers": {pid: p.model_dump() for pid, p in self.papers.items()},
            "entities": {eid: e.model_dump() for eid, e in self.entities.items()},
            "relations": [r.model_dump() for r in self.relations],
            "summary": self.get_summary().model_dump()
        }
        
    def to_json(self, filepath: str):
        """导出为JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2, default=str)
            
    def to_graphml(self, filepath: str):
        """导出为GraphML格式 (可用于Cytoscape)"""
        nx.write_graphml(self.graph, filepath)
        
    def get_subgraph(self, node_ids: List[str], depth: int = 1) -> 'KnowledgeGraph':
        """提取子图"""
        subgraph_kg = KnowledgeGraph()
        
        # 获取指定深度内的所有节点
        nodes_to_include = set(node_ids)
        for _ in range(depth):
            new_nodes = set()
            for node in nodes_to_include:
                if node in self.graph:
                    new_nodes.update(self.graph.predecessors(node))
                    new_nodes.update(self.graph.successors(node))
            nodes_to_include.update(new_nodes)
            
        # 添加节点
        for node_id in nodes_to_include:
            if node_id in self.papers:
                subgraph_kg.add_paper(self.papers[node_id])
            elif node_id in self.entities:
                subgraph_kg.add_entity(self.entities[node_id])
                
        # 添加关系
        for relation in self.relations:
            if (relation.source_id in nodes_to_include and 
                relation.target_id in nodes_to_include):
                subgraph_kg.add_relation(relation)
                
        return subgraph_kg

