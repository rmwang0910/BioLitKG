"""
工作流程分析器

专门用于从文献中提取分析流程、方法步骤,并生成最佳实践建议
"""
import logging
import os
from typing import List, Dict, Optional, Any, Set
from pathlib import Path
from collections import Counter, defaultdict

from literature.base_client import PaperMetadata
from core.llm.openai import OpenAIProvider
from core.config import get_config

logger = logging.getLogger(__name__)


class WorkflowStep:
    """工作流程步骤"""
    def __init__(self, name: str, description: str, tools: List[str], papers: List[str]):
        self.name = name
        self.description = description
        self.tools = tools  # 使用的工具/方法
        self.papers = papers  # 来源论文
        self.order = None  # 步骤顺序
        
    def __repr__(self):
        return f"Step({self.name})"


class WorkflowAnalyzer:
    """
    生信工作流程分析器
    
    用于从文献中提取标准分析流程,识别工具,生成最佳实践
    
    Parameters:
        use_llm: 是否使用LLM生成分析报告 (默认: True)
        max_papers: 最多分析的论文数量 (默认: 100)
        min_citations: 最少引用数筛选 (默认: None,不筛选)
        year_from: 起始年份 (默认: None,不限制)
        year_to: 结束年份 (默认: None,不限制)
    
    Example:
        ```python
        analyzer = WorkflowAnalyzer(
            use_llm=True,
            max_papers=50,
            min_citations=20,
            year_from=2020
        )
        
        # 分析单细胞RNA-seq工作流程
        result = analyzer.analyze_workflow(papers, workflow_type="scrna_seq")
        
        # 生成报告
        analyzer.generate_workflow_report(result, "output/report.md")
        ```
    """
    
    # 单细胞RNA-seq常见步骤关键词
    SCRNA_WORKFLOW_STEPS = {
        'quality_control': ['quality control', 'QC', 'filtering', 'doublet removal'],
        'normalization': ['normalization', 'scaling', 'log normalization'],
        'feature_selection': ['feature selection', 'highly variable genes', 'HVG'],
        'dimensionality_reduction': ['PCA', 'dimensionality reduction', 't-SNE', 'UMAP'],
        'clustering': ['clustering', 'cell clustering', 'Louvain', 'Leiden'],
        'cell_annotation': ['cell type annotation', 'marker genes', 'cell identification'],
        'differential_expression': ['differential expression', 'DEG', 'DE analysis'],
        'trajectory_analysis': ['trajectory', 'pseudotime', 'lineage'],
    }
    
    # 常用工具/软件
    COMMON_TOOLS = [
        'Seurat', 'Scanpy', 'Cell Ranger', 'STAR', 'Kallisto',
        'Monocle', 'Velocyto', 'SingleR', 'scVI', 'Harmony',
        'CellPhoneDB', 'CellChat', 'Scrublet', 'DoubletFinder'
    ]
    
    def __init__(
        self,
        use_llm: bool = True,
        max_papers: int = 100,
        min_citations: Optional[int] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None
    ):
        """初始化工作流程分析器"""
        self.use_llm = use_llm
        self.max_papers = max_papers
        self.min_citations = min_citations
        self.year_from = year_from
        self.year_to = year_to
        
        if use_llm:
            try:
                config = get_config()
                self.llm_client = OpenAIProvider(config.llm)
            except Exception as e:
                logger.warning(f"无法初始化LLM: {e}")
                self.use_llm = False
    
    def analyze_workflow(
        self,
        papers: List[PaperMetadata],
        workflow_type: str = "scrna_seq"
    ) -> Dict[str, Any]:
        """
        从文献中分析工作流程
        
        Args:
            papers: 论文列表
            workflow_type: 工作流程类型 (scrna_seq, bulk_rna_seq等)
            
        Returns:
            工作流程分析结果
        """
        # 应用筛选条件
        filtered_papers = self._filter_papers(papers)
        logger.info(f"分析 {len(filtered_papers)} 篇论文的工作流程...")
        
        # 1. 提取步骤
        steps = self._extract_workflow_steps(filtered_papers)
        logger.info(f"识别了 {len(steps)} 个工作流程步骤")
        
        # 2. 提取工具
        tools = self._extract_tools(filtered_papers)
        logger.info(f"识别了 {len(tools)} 个工具/软件")
        
        # 3. 构建步骤依赖关系
        step_graph = self._build_step_dependencies(steps, filtered_papers)
        
        # 4. 使用LLM生成最佳实践 (可选)
        best_practices = None
        if self.use_llm:
            best_practices = self._generate_best_practices(filtered_papers, steps, tools)
        
        return {
            'steps': steps,
            'tools': tools,
            'step_graph': step_graph,
            'best_practices': best_practices,
            'paper_count': len(filtered_papers)
        }
    
    def _filter_papers(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        """根据设定条件筛选论文"""
        filtered = papers
        
        logger.info(f"开始筛选: {len(filtered)} 篇论文")
        
        # 按引用数筛选
        if self.min_citations:
            before = len(filtered)
            filtered = [p for p in filtered if p.citation_count and p.citation_count >= self.min_citations]
            logger.info(f"引用数筛选(>={self.min_citations}): {before} -> {len(filtered)} 篇")
        
        # 按年份筛选
        if self.year_from:
            before = len(filtered)
            filtered = [p for p in filtered if p.year and p.year >= self.year_from]
            logger.info(f"年份筛选(>={self.year_from}): {before} -> {len(filtered)} 篇")
        if self.year_to:
            before = len(filtered)
            filtered = [p for p in filtered if p.year and p.year <= self.year_to]
            logger.info(f"年份筛选(<={self.year_to}): {before} -> {len(filtered)} 篇")
        
        # 限制数量
        if len(filtered) > self.max_papers:
            # 按引用数排序后取前N篇
            filtered = sorted(filtered, key=lambda p: p.citation_count or 0, reverse=True)[:self.max_papers]
            logger.info(f"数量限制: 取前{self.max_papers}篇")
        
        logger.info(f"最终筛选结果: {len(filtered)} 篇论文")
        
        return filtered
    
    def _extract_workflow_steps(
        self,
        papers: List[PaperMetadata]
    ) -> Dict[str, WorkflowStep]:
        """从论文中提取工作流程步骤"""
        
        step_mentions = defaultdict(lambda: {
            'count': 0, 
            'papers': [], 
            'contexts': [],
            'paper_details': []  # 新增:保存论文详情
        })
        
        # 创建paper_id到paper对象的映射
        paper_map = {}
        for paper in papers:
            paper_id = paper.doi or paper.arxiv_id or paper.pubmed_id or paper.id
            paper_map[paper_id] = paper
        
        for paper in papers:
            text = f"{paper.title} {paper.abstract}".lower()
            original_text = f"{paper.title} {paper.abstract}"  # 保留原文
            paper_id = paper.doi or paper.arxiv_id or paper.pubmed_id or paper.id
            
            # 检查每个步骤的关键词
            for step_name, keywords in self.SCRNA_WORKFLOW_STEPS.items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        step_mentions[step_name]['count'] += 1
                        
                        # 保存论文详情(避免重复)
                        if paper_id not in step_mentions[step_name]['papers']:
                            step_mentions[step_name]['papers'].append(paper_id)
                            
                            # 提取包含关键词的完整句子
                            idx = original_text.find(keyword)
                            if idx == -1:
                                idx = original_text.lower().find(keyword.lower())
                            
                            # 向前找到句子开始
                            start = idx
                            while start > 0 and original_text[start] not in '.!?\n':
                                start -= 1
                            if start > 0:
                                start += 1  # 跳过句号
                            
                            # 向后找到句子结束
                            end = idx + len(keyword)
                            while end < len(original_text) and original_text[end] not in '.!?\n':
                                end += 1
                            if end < len(original_text):
                                end += 1  # 包含句号
                            
                            # 提取句子
                            sentence = original_text[start:end].strip()
                            
                            # 保存详细信息
                            step_mentions[step_name]['paper_details'].append({
                                'paper': paper,
                                'sentence': sentence,
                                'keyword': keyword
                            })
                        break
        
        # 构建WorkflowStep对象,保存详细信息
        steps = {}
        for step_name, data in step_mentions.items():
            if data['count'] > 0:
                description = f"在 {len(data['papers'])} 篇论文中提到 {data['count']} 次"
                
                step = WorkflowStep(
                    name=step_name.replace('_', ' ').title(),
                    description=description,
                    tools=[],
                    papers=data['papers']
                )
                # 附加详细信息
                step.paper_details = data['paper_details']
                
                steps[step_name] = step
        
        return steps
    
    def _extract_tools(self, papers: List[PaperMetadata]) -> Dict[str, List[str]]:
        """提取工具和软件"""
        
        tool_mentions = defaultdict(lambda: {'count': 0, 'papers': []})
        
        for paper in papers:
            text = f"{paper.title} {paper.abstract}"
            paper_id = paper.doi or paper.arxiv_id or paper.pubmed_id or paper.id
            
            for tool in self.COMMON_TOOLS:
                if tool in text:
                    tool_mentions[tool]['count'] += 1
                    if paper_id not in tool_mentions[tool]['papers']:
                        tool_mentions[tool]['papers'].append(paper_id)
        
        # 按提及次数排序
        tools = {
            tool: data['papers']
            for tool, data in sorted(
                tool_mentions.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
            if data['count'] > 0
        }
        
        return tools
    
    def _build_step_dependencies(
        self,
        steps: Dict[str, WorkflowStep],
        papers: List[PaperMetadata]
    ) -> Dict[str, List[str]]:
        """构建步骤间的依赖关系"""
        
        # 标准单细胞分析流程的典型顺序
        standard_order = [
            'quality_control',
            'normalization',
            'feature_selection',
            'dimensionality_reduction',
            'clustering',
            'cell_annotation',
            'differential_expression',
            'trajectory_analysis'
        ]
        
        dependencies = {}
        for i, step in enumerate(standard_order):
            if step in steps:
                steps[step].order = i
                if i > 0:
                    prev_steps = [s for s in standard_order[:i] if s in steps]
                    dependencies[step] = prev_steps
                else:
                    dependencies[step] = []
        
        return dependencies
    
    def _generate_best_practices(
        self,
        papers: List[PaperMetadata],
        steps: Dict[str, WorkflowStep],
        tools: Dict[str, List[str]]
    ) -> str:
        """使用LLM生成最佳实践建议"""
        
        if not self.use_llm:
            return None
        
        # 准备论文摘要
        paper_summaries = []
        for i, paper in enumerate(papers[:10], 1):
            summary = f"{i}. {paper.title} ({paper.year})\n"
            summary += f"   引用数: {paper.citation_count}\n"
            if paper.abstract:
                summary += f"   摘要: {paper.abstract[:200]}...\n"
            paper_summaries.append(summary)
        
        # 步骤列表
        step_list = "\n".join([
            f"- {step.name}: {step.description}"
            for step in sorted(steps.values(), key=lambda s: s.order or 999)
        ])
        
        # 工具列表
        tool_list = "\n".join([
            f"- {tool}: 在{len(paper_ids)}篇论文中提及"
            for tool, paper_ids in list(tools.items())[:10]
        ])
        
        prompt = f"""基于以下单细胞RNA测序(scRNA-seq)分析相关的高引文献,总结最佳的数据分析流程。

相关论文 (按引用数排序):
{chr(10).join(paper_summaries)}

识别到的分析步骤:
{step_list}

常用工具:
{tool_list}

请提供:
1. 标准的scRNA-seq数据分析流程(步骤顺序)
2. 每个步骤的关键要点和注意事项
3. 推荐的工具/软件
4. 常见的质量控制标准
5. 最新的最佳实践建议

请用结构化的Markdown格式输出,包含清晰的步骤编号和要点。
"""
        
        try:
            logger.info("正在使用LLM生成最佳实践建议...")
            response = self.llm_client.generate(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.3
            )
            return response
            
        except Exception as e:
            logger.error(f"LLM生成失败: {e}")
            return None
    
    def generate_workflow_report(
        self,
        workflow_result: Dict[str, Any],
        output_path: str
    ):
        """生成工作流程报告"""
        
        steps = workflow_result['steps']
        tools = workflow_result['tools']
        best_practices = workflow_result.get('best_practices')
        
        report = f"""# 单细胞RNA-seq数据分析工作流程报告

## 分析参数

- **分析论文数**: {workflow_result['paper_count']}
- **识别步骤数**: {len(steps)}
- **识别工具数**: {len(tools)}

**筛选条件**:
- 最多分析论文: {self.max_papers}
- 最少引用数: {self.min_citations or '无限制'}
- 起始年份: {self.year_from or '不限'}
- 结束年份: {self.year_to or '不限'}

## 分析流程步骤

"""
        
        # 按顺序输出步骤
        sorted_steps = sorted(steps.values(), key=lambda s: s.order or 999)
        for i, step in enumerate(sorted_steps, 1):
            report += f"### {i}. {step.name}\n\n"
            report += f"- **描述**: {step.description}\n"
            report += f"- **相关论文数**: {len(step.papers)}\n\n"
            
            # 添加详细的论文引用
            if hasattr(step, 'paper_details') and step.paper_details:
                report += f"**相关论文及引用**:\n\n"
                for detail in step.paper_details[:5]:  # 最多显示5篇
                    paper = detail['paper']
                    sentence = detail['sentence']
                    
                    # 论文标题
                    report += f"**[{i}.{step.paper_details.index(detail)+1}] {paper.title}**\n\n"
                    
                    # 论文信息
                    report += f"- 作者: "
                    if paper.authors:
                        author_names = []
                        for a in paper.authors[:3]:
                            if isinstance(a, str):
                                author_names.append(a)
                            else:
                                author_names.append(a.name if hasattr(a, 'name') else str(a))
                        report += ', '.join(author_names)
                        if len(paper.authors) > 3:
                            report += ' 等'
                    report += "\n"
                    
                    report += f"- 年份: {paper.year or 'N/A'}\n"
                    report += f"- 引用数: {paper.citation_count or 0}\n"
                    
                    # 链接
                    if paper.doi:
                        report += f"- DOI: [{paper.doi}](https://doi.org/{paper.doi})\n"
                    if paper.arxiv_id:
                        report += f"- arXiv: [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})\n"
                    if paper.pubmed_id:
                        report += f"- PubMed: [PMID:{paper.pubmed_id}](https://pubmed.ncbi.nlm.nih.gov/{paper.pubmed_id}/)\n"
                    
                    # 相关句子
                    if sentence:
                        report += f"- **提及内容**: \"{sentence}\"\n"
                    
                    report += "\n"
            
            report += "\n"
        
        report += "## 常用工具/软件\n\n"
        report += "| 工具 | 提及论文数 | 推荐度 |\n"
        report += "|------|----------|--------|\n"
        
        for tool, paper_ids in list(tools.items())[:15]:
            stars = "⭐" * min(5, len(paper_ids))
            report += f"| {tool} | {len(paper_ids)} | {stars} |\n"
        
        if best_practices:
            report += f"\n## 最佳实践建议 (AI生成)\n\n"
            report += best_practices
            report += "\n"
        
        report += f"\n---\n\n*报告生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"工作流程报告已保存到: {output_path}")
        
        return report

