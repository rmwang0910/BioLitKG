"""
工作流程可视化器

专门用于创建清晰的分析流程图和网络图
"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict

try:
    from pyvis.network import Network
    import plotly.graph_objects as go
    import networkx as nx
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    logging.warning("可视化库不可用,请安装: pip install pyvis plotly networkx")

logger = logging.getLogger(__name__)


class WorkflowVisualizer:
    """工作流程可视化器"""
    
    # 步骤颜色方案
    STEP_COLORS = {
        'quality_control': '#FF6B6B',
        'normalization': '#4ECDC4',
        'feature_selection': '#45B7D1',
        'dimensionality_reduction': '#96CEB4',
        'clustering': '#FFEAA7',
        'cell_annotation': '#DFE6E9',
        'differential_expression': '#74B9FF',
        'trajectory_analysis': '#A29BFE'
    }
    
    def create_workflow_network(
        self,
        workflow_result: Dict[str, Any],
        papers: List[Any],
        output_path: str
    ):
        """
        创建工作流程网络图(步骤+工具+论文)
        
        Args:
            workflow_result: 工作流程分析结果
            papers: 论文列表
            output_path: 输出路径
        """
        if not VISUALIZATION_AVAILABLE:
            logger.error("可视化库不可用,请安装: pip install pyvis plotly networkx")
            return
        
        steps = workflow_result['steps']
        tools = workflow_result['tools']
        
        # 创建网络
        net = Network(
            height="900px",
            width="100%",
            bgcolor="#fafafa",
            font_color="#000000",
            directed=False
        )
        
        # 物理引擎配置
        net.set_options("""
        {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 150,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 200}
          }
        }
        """)
        
        # 1. 添加步骤节点(核心,最大)
        added_nodes = set()
        for step in steps.values():
            step_id = f"step:{step.name}"
            step_key = step.name.lower().replace(' ', '_')
            color = self.STEP_COLORS.get(step_key, '#95A5A6')
            
            net.add_node(
                step_id,
                label=step.name,
                title=f"<b>{step.name}</b><br>{step.description}",
                color=color,
                size=40,
                shape="box",
                font={'size': 16, 'color': '#000000'}
            )
            added_nodes.add(step_id)
        
        # 2. 添加工具节点(中等大小)
        for tool, tool_papers in list(tools.items())[:15]:
            tool_id = f"tool:{tool}"
            size = 15 + len(tool_papers) * 2
            
            net.add_node(
                tool_id,
                label=tool,
                title=f"<b>{tool}</b><br>在{len(tool_papers)}篇论文中提及",
                color='#FF9F43',
                size=size,
                shape="ellipse",
                font={'size': 12, 'color': '#000000'}
            )
            added_nodes.add(tool_id)
        
        # 3. 添加论文节点(小,只显示前15篇)
        top_papers = sorted(papers, key=lambda p: p.citation_count or 0, reverse=True)[:15]
        
        for paper in top_papers:
            paper_id = f"paper:{paper.id or paper.doi or paper.arxiv_id}"
            title = paper.title[:50] + "..." if len(paper.title) > 50 else paper.title
            size = 10 + min((paper.citation_count or 0) / 50, 15)
            
            net.add_node(
                paper_id,
                label=title[:20] + "...",
                title=f"<b>{paper.title}</b><br>引用数: {paper.citation_count}<br>年份: {paper.year}",
                color='#3498DB',
                size=size,
                shape="dot",
                font={'size': 10, 'color': '#000000'}
            )
            added_nodes.add(paper_id)
        
        # 4. 添加边: 步骤之间的顺序关系
        sorted_steps_list = sorted(steps.values(), key=lambda s: s.order or 999)
        for i in range(len(sorted_steps_list) - 1):
            from_id = f"step:{sorted_steps_list[i].name}"
            to_id = f"step:{sorted_steps_list[i+1].name}"
            if from_id in added_nodes and to_id in added_nodes:
                net.add_edge(
                    from_id,
                    to_id,
                    color='#2C3E50',
                    width=4,
                    title="流程顺序"
                )
        
        # 5. 添加边: 步骤 - 工具
        for step in steps.values():
            step_id = f"step:{step.name}"
            step_paper_ids = set(step.papers)
            
            for tool, tool_papers in list(tools.items())[:15]:
                tool_id = f"tool:{tool}"
                # 计算共同论文数
                common = len(set(tool_papers) & step_paper_ids)
                
                if common >= 1 and step_id in added_nodes and tool_id in added_nodes:
                    net.add_edge(
                        step_id,
                        tool_id,
                        value=common,
                        title=f"{common}篇论文关联",
                        color='rgba(52, 152, 219, 0.5)',
                        width=1 + common
                    )
        
        # 6. 添加边: 工具 - 论文
        for paper in top_papers:
            paper_id = f"paper:{paper.id or paper.doi or paper.arxiv_id}"
            if paper_id not in added_nodes:
                continue
                
            text = f"{paper.title} {paper.abstract}".lower() if paper.abstract else paper.title.lower()
            
            for tool in list(tools.keys())[:15]:
                tool_id = f"tool:{tool}"
                # 检查论文中是否提到这个工具
                if tool.lower() in text and tool_id in added_nodes:
                    net.add_edge(
                        tool_id,
                        paper_id,
                        color='rgba(149, 165, 166, 0.3)',
                        width=1,
                        title=f"{paper.title[:40]}... 使用了 {tool}"
                    )
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        net.save_graph(str(output_path))
        
        logger.info(f"工作流程网络图已保存到: {output_path}")
    
    def create_tool_comparison_chart(
        self,
        workflow_result: Dict[str, Any],
        output_path: str
    ):
        """
        创建工具对比图表
        
        Args:
            workflow_result: 工作流程分析结果
            output_path: 输出路径
        """
        if not VISUALIZATION_AVAILABLE:
            logger.error("可视化库不可用")
            return
        
        tools = workflow_result['tools']
        
        # 准备数据
        tool_names = list(tools.keys())[:15]
        tool_counts = [len(papers) for papers in list(tools.values())[:15]]
        
        # 创建柱状图
        fig = go.Figure(data=[
            go.Bar(
                x=tool_counts,
                y=tool_names,
                orientation='h',
                marker=dict(
                    color=tool_counts,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="提及次数")
                ),
                text=tool_counts,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title={
                'text': '单细胞RNA-seq常用工具/软件排名',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='提及论文数量',
            yaxis_title='工具/软件',
            height=600,
            template='plotly_white'
        )
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        
        logger.info(f"工具对比图表已保存到: {output_path}")
    
    def create_paper_statistics(
        self,
        papers: List[Any],
        output_path: str
    ):
        """
        创建论文统计图表
        
        Args:
            papers: 论文列表
            output_path: 输出路径
        """
        if not VISUALIZATION_AVAILABLE:
            logger.error("可视化库不可用")
            return
        
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '论文年份分布',
                '引用数分布',
                '年份-引用数关系',
                'Top 10 高引论文'
            )
        )
        
        # 1. 年份分布
        years = [p.year for p in papers if p.year]
        year_counts = {}
        for year in years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        fig.add_trace(
            go.Bar(x=list(year_counts.keys()), y=list(year_counts.values()), name='论文数'),
            row=1, col=1
        )
        
        # 2. 引用数分布
        citations = [p.citation_count for p in papers if hasattr(p, 'citation_count') and p.citation_count]
        if citations:
            fig.add_trace(
                go.Histogram(x=citations, nbinsx=20, name='引用数'),
                row=1, col=2
            )
        else:
            # 如果没有引用数据，显示提示文本
            fig.add_annotation(
                text="暂无引用数据<br>请使用 --enrich-citations 选项补充",
                xref="x2", yref="y2",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray"),
                row=1, col=2
            )
        
        # 3. 年份-引用数散点图
        years_cit = [(p.year, p.citation_count) for p in papers 
                     if p.year and hasattr(p, 'citation_count') and p.citation_count]
        if years_cit:
            y, c = zip(*years_cit)
            fig.add_trace(
                go.Scatter(x=y, y=c, mode='markers', name='论文',
                          marker=dict(size=8, opacity=0.6)),
                row=2, col=1
            )
        else:
            # 如果没有数据，显示提示文本
            fig.add_annotation(
                text="暂无引用数据<br>请使用 --enrich-citations 选项补充",
                xref="x3", yref="y3",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=14, color="gray"),
                row=2, col=1
            )
        
        # 4. Top 10
        # 获取有引用数的论文
        papers_with_citations = [p for p in papers if hasattr(p, 'citation_count') and p.citation_count]
        
        if papers_with_citations:
            top_papers = sorted(papers_with_citations, key=lambda p: p.citation_count or 0, reverse=True)[:10]
            titles = [p.title[:30] + "..." for p in top_papers]
            cit_counts = [p.citation_count or 0 for p in top_papers]
            
            fig.add_trace(
                go.Bar(y=titles[::-1], x=cit_counts[::-1], orientation='h', name='引用数'),
                row=2, col=2
            )
        else:
            # 如果没有引用数据，显示最近的10篇论文
            recent_papers = sorted(papers, key=lambda p: p.year or 0, reverse=True)[:10]
            titles = [p.title[:30] + "..." for p in recent_papers]
            years_list = [p.year or 0 for p in recent_papers]
            
            fig.add_trace(
                go.Bar(y=titles[::-1], x=years_list[::-1], orientation='h', name='年份'),
                row=2, col=2
            )
            
            # 更新子图标题
            fig.layout.annotations[3].update(text='Top 10 最新论文')
        
        # 更新布局
        fig.update_layout(height=900, showlegend=False, title_text="论文统计分析")
        fig.update_xaxes(title_text="年份", row=1, col=1)
        fig.update_yaxes(title_text="论文数", row=1, col=1)
        fig.update_xaxes(title_text="引用数", row=1, col=2)
        fig.update_yaxes(title_text="频次", row=1, col=2)
        fig.update_xaxes(title_text="年份", row=2, col=1)
        fig.update_yaxes(title_text="引用数", row=2, col=1)
        
        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        
        logger.info(f"统计图表已保存到: {output_path}")

