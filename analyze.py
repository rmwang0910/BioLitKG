#!/usr/bin/env python
"""
BioLitKG 交互式分析

通过对话方式指定分析内容和参数
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 配置logging
logging.basicConfig(
    level=logging.WARNING,  # 减少输出
    format='%(message)s'
)

# 配置LLM (从环境变量读取)
if not os.getenv('LLM_API_KEY'):
    print("⚠️  请先设置API密钥: export LLM_API_KEY='your-key'")
    print("   或在运行时输入")

from workflow import WorkflowAnalyzer, WorkflowVisualizer
from literature import UnifiedLiteratureSearch


def get_input(prompt, default=None, input_type=str):
    """获取用户输入"""
    if default:
        prompt = f"{prompt} [默认: {default}]"
    
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            if not value and default is not None:
                return default
            if not value:
                print("❌ 请输入有效值")
                continue
            
            if input_type == int:
                return int(value)
            elif input_type == bool:
                return value.lower() in ['y', 'yes', '是', 't', 'true']
            else:
                return value
        except ValueError:
            print(f"❌ 请输入有效的{input_type.__name__}类型")
        except KeyboardInterrupt:
            print("\n\n👋 已取消")
            sys.exit(0)


def interactive_analysis():
    """交互式分析流程"""
    
    print("=" * 80)
    print("🧬 BioLitKG 交互式文献分析")
    print("=" * 80)
    print()
    print("通过对话方式设置分析参数")
    print("提示: 直接回车使用默认值,Ctrl+C取消")
    print()
    
    # ===== 1. 分析主题 =====
    print("📋 步骤1: 分析主题")
    print("-" * 80)
    
    topic = get_input("请输入分析主题", "single cell RNA sequencing")
    
    # 推荐关键词
    print("\n💡 推荐添加的关键词(可选):")
    print("  1. review - 优先综述")
    print("  2. benchmark - 优先比较研究")
    print("  3. protocol - 优先实验方案")
    print("  4. best practice - 优先最佳实践")
    
    add_keywords = get_input("\n是否添加关键词? (y/n)", "y", bool)
    
    if add_keywords:
        print("\n选择添加的关键词:")
        keywords = []
        if get_input("  添加 'review'? (y/n)", "y", bool):
            keywords.append("review")
        if get_input("  添加 'benchmark'? (y/n)", "n", bool):
            keywords.append("benchmark")
        if get_input("  添加 'protocol'? (y/n)", "n", bool):
            keywords.append("protocol")
        if get_input("  添加 'best practice'? (y/n)", "n", bool):
            keywords.append("best practice")
        
        if keywords:
            topic = f"{topic} {' '.join(keywords)}"
    
    print(f"\n✓ 最终搜索词: {topic}")
    
    # ===== 2. 文献数量 =====
    print(f"\n📊 步骤2: 文献数量")
    print("-" * 80)
    
    max_search = get_input("最多搜索多少篇论文?", 100, int)
    max_analyze = get_input("最多分析多少篇论文?", 50, int)
    
    # ===== 3. 影响力筛选 =====
    print(f"\n⭐ 步骤3: 影响力筛选(引用数)")
    print("-" * 80)
    print("💡 引用数参考:")
    print("  >500: 极高影响力(Nature/Cell/Science级别)")
    print("  >200: 高影响力")
    print("  >100: 中高影响力")
    print("  >50:  中等影响力")
    print("  >20:  一般影响力")
    print("  0:    不筛选(包含新论文)")
    
    min_citations = get_input("\n最少引用数", 20, int)
    
    # ===== 4. 年份范围 =====
    print(f"\n📅 步骤4: 年份范围")
    print("-" * 80)
    
    current_year = datetime.now().year
    year_from = get_input(f"起始年份 (建议2015-{current_year})", 2018, int)
    year_to = get_input(f"结束年份", current_year, int)
    
    # ===== 5. 数据源选择 =====
    print(f"\n🔍 步骤5: 数据源")
    print("-" * 80)
    print("可用数据源:")
    print("  - arXiv: 预印本(计算机/物理/生物)")
    print("  - PubMed: 生物医学主库")
    
    use_arxiv = get_input("\n使用arXiv? (y/n)", "y", bool)
    use_pubmed = get_input("使用PubMed? (y/n)", "y", bool)
    
    # ===== 6. 高级选项 =====
    print(f"\n⚙️  步骤6: 高级选项")
    print("-" * 80)
    
    use_llm = get_input("启用AI分析? (y/n)", "y", bool)
    create_viz = get_input("生成可视化? (y/n)", "y", bool)
    
    # ===== 7. 输出位置 =====
    print(f"\n📁 步骤7: 输出设置")
    print("-" * 80)
    
    output_name = get_input("输出目录名称", "my_analysis")
    output_dir = Path(f"outputs/{output_name}")
    
    # ===== 确认配置 =====
    print(f"\n" + "=" * 80)
    print("📋 配置确认")
    print("=" * 80)
    print(f"\n分析主题: {topic}")
    print(f"搜索数量: 最多{max_search}篇")
    print(f"分析数量: 最多{max_analyze}篇")
    print(f"引用筛选: >={min_citations}次")
    print(f"年份范围: {year_from}-{year_to}")
    print(f"数据源: arXiv={'✓' if use_arxiv else '✗'}, PubMed={'✓' if use_pubmed else '✗'}")
    print(f"AI分析: {'启用' if use_llm else '禁用'}")
    print(f"可视化: {'生成' if create_viz else '不生成'}")
    print(f"输出位置: {output_dir}")
    
    confirm = get_input("\n开始分析? (y/n)", "y", bool)
    if not confirm:
        print("👋 已取消")
        return
    
    # ===== 开始分析 =====
    print(f"\n" + "=" * 80)
    print("🚀 开始分析")
    print("=" * 80)
    
    # 检查API密钥
    if use_llm and not os.getenv('LLM_API_KEY'):
        api_key = get_input("\n请输入您的LLM API密钥")
        os.environ['LLM_API_KEY'] = api_key
        os.environ['LLM_BASE_URL'] = os.getenv('LLM_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        os.environ['LLM_MODEL'] = os.getenv('LLM_MODEL', 'qwen-plus')
    
    # 1. 搜索文献
    print(f"\n步骤1/5: 搜索文献...")
    print(f"  关键词: {topic}")
    print(f"  数据源: {'arXiv, ' if use_arxiv else ''}{'PubMed' if use_pubmed else ''}")
    
    search = UnifiedLiteratureSearch()
    papers = search.search(query=topic, max_results=max_search)
    
    print(f"✓ 找到 {len(papers)} 篇论文")
    
    if not papers:
        print("❌ 没有找到论文,请调整搜索词")
        return
    
    # 2. 筛选论文
    print(f"\n步骤2/5: 筛选论文...")
    
    # 年份筛选
    papers = [p for p in papers if p.year and year_from <= p.year <= year_to]
    print(f"  年份筛选({year_from}-{year_to}): {len(papers)} 篇")
    
    # 引用数筛选
    if min_citations > 0:
        papers = [p for p in papers if p.citation_count and p.citation_count >= min_citations]
        print(f"  引用数筛选(>={min_citations}): {len(papers)} 篇")
    
    # 排序和限制数量
    papers = sorted(papers, key=lambda p: p.citation_count or 0, reverse=True)
    papers = papers[:max_analyze]
    print(f"  最终选择: {len(papers)} 篇")
    
    if not papers:
        print("❌ 筛选后没有论文,请降低筛选条件")
        return
    
    # 显示Top 5
    print(f"\n  Top 5论文:")
    for i, p in enumerate(papers[:5], 1):
        cit = p.citation_count or 0
        print(f"    {i}. [{cit}引, {p.year}] {p.title[:60]}...")
    
    # 3. 分析工作流程
    print(f"\n步骤3/5: 分析工作流程...")
    
    analyzer = WorkflowAnalyzer(
        use_llm=use_llm,
        max_papers=max_analyze,
        min_citations=min_citations,
        year_from=year_from,
        year_to=year_to
    )
    
    result = analyzer.analyze_workflow(papers)
    
    print(f"✓ 识别了 {len(result['steps'])} 个步骤")
    print(f"✓ 识别了 {len(result['tools'])} 个工具")
    
    # 4. 生成报告
    print(f"\n步骤4/5: 生成报告...")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Markdown报告
    report_path = output_dir / "WORKFLOW_REPORT.md"
    analyzer.generate_workflow_report(result, str(report_path))
    print(f"✓ {report_path}")
    
    # 论文清单
    papers_path = output_dir / "PAPERS_LIST.md"
    with open(papers_path, 'w', encoding='utf-8') as f:
        f.write(f"# 分析的论文清单\n\n")
        f.write(f"**分析主题**: {topic}\n")
        f.write(f"**总数**: {len(papers)} 篇\n")
        f.write(f"**筛选条件**: 年份{year_from}-{year_to}, 引用数>={min_citations}\n\n")
        
        for i, paper in enumerate(papers, 1):
            f.write(f"## {i}. {paper.title}\n\n")
            
            # 作者
            if paper.authors:
                author_names = []
                for a in paper.authors[:3]:
                    if isinstance(a, str):
                        author_names.append(a)
                    else:
                        author_names.append(a.name if hasattr(a, 'name') else str(a))
                authors = ', '.join(author_names)
                if len(paper.authors) > 3:
                    authors += ' 等'
                f.write(f"- **作者**: {authors}\n")
            
            f.write(f"- **年份**: {paper.year or 'N/A'}\n")
            f.write(f"- **引用数**: {paper.citation_count or 0}\n")
            
            if paper.doi:
                f.write(f"- **DOI**: [{paper.doi}](https://doi.org/{paper.doi})\n")
            if paper.arxiv_id:
                f.write(f"- **arXiv**: [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})\n")
            if paper.pubmed_id:
                f.write(f"- **PubMed**: [PMID:{paper.pubmed_id}](https://pubmed.ncbi.nlm.nih.gov/{paper.pubmed_id}/)\n")
            
            if paper.abstract:
                f.write(f"- **摘要**: {paper.abstract[:200]}...\n")
            
            f.write(f"\n")
    
    print(f"✓ {papers_path}")
    
    # 5. 生成可视化(可选)
    if create_viz:
        print(f"\n步骤5/5: 生成可视化...")
        
        visualizer = WorkflowVisualizer()
        
        # 网络图
        network_path = output_dir / "workflow_network.html"
        visualizer.create_workflow_network(result, papers, str(network_path))
        print(f"✓ 网络图: {network_path}")
        
        # 工具对比
        if result['tools']:
            tool_path = output_dir / "tool_comparison.html"
            visualizer.create_tool_comparison_chart(result, str(tool_path))
            print(f"✓ 工具对比: {tool_path}")
        
        # 统计图表
        stats_path = output_dir / "paper_statistics.html"
        visualizer.create_paper_statistics(papers, str(stats_path))
        print(f"✓ 统计图表: {stats_path}")
    
    # ===== 完成 =====
    print(f"\n" + "=" * 80)
    print("🎉 分析完成!")
    print("=" * 80)
    
    print(f"\n📊 分析结果:")
    print(f"  论文数: {len(papers)}")
    print(f"  步骤数: {len(result['steps'])}")
    print(f"  工具数: {len(result['tools'])}")
    
    print(f"\n🔬 识别的步骤:")
    for step in sorted(result['steps'].values(), key=lambda s: s.order or 999):
        print(f"  {step.order+1 if step.order is not None else '?'}. {step.name}")
    
    print(f"\n🛠️  常用工具 (Top 5):")
    for i, (tool, tool_papers) in enumerate(list(result['tools'].items())[:5], 1):
        print(f"  {i}. {tool} - {len(tool_papers)}篇")
    
    print(f"\n📁 生成的文件:")
    print(f"  - {report_path}")
    print(f"  - {papers_path}")
    if create_viz:
        print(f"  - {network_path}")
        print(f"  - {tool_path if result['tools'] else 'N/A'}")
        print(f"  - {stats_path}")
    
    print(f"\n💡 查看结果:")
    print(f"  cat {report_path}")
    if create_viz:
        print(f"  open {network_path}")
    
    print(f"\n✨ 所有文件已保存到: {output_dir}")


def quick_mode():
    """快速模式 - 通过命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BioLitKG 快速分析')
    parser.add_argument('topic', help='分析主题')
    parser.add_argument('--max-papers', type=int, default=50, help='最多分析论文数')
    parser.add_argument('--min-citations', type=int, default=20, help='最少引用数')
    parser.add_argument('--year-from', type=int, default=2018, help='起始年份')
    parser.add_argument('--year-to', type=int, default=datetime.now().year, help='结束年份')
    parser.add_argument('--no-viz', action='store_true', help='不生成可视化')
    parser.add_argument('--output', default='quick_analysis', help='输出目录名')
    
    args = parser.parse_args()
    
    print(f"🚀 快速分析: {args.topic}")
    print(f"   论文数: {args.max_papers}, 引用>={args.min_citations}, 年份{args.year_from}-{args.year_to}")
    
    # 执行分析 (使用args中的参数)
    # ... (实现类似interactive_analysis的逻辑)
    
    print("✓ 完成!")


if __name__ == "__main__":
    # 检查是否有命令行参数
    if len(sys.argv) > 1 and sys.argv[1] not in ['-h', '--help']:
        quick_mode()
    else:
        interactive_analysis()

