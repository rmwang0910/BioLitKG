#!/usr/bin/env python3
"""
BioLitKG 大规模分析测试脚本
直接运行,无需交互式输入
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from literature import UnifiedLiteratureSearch
from workflow import WorkflowAnalyzer
from workflow.visualizer import WorkflowVisualizer
from utils import CitationEnricher


def print_banner(text):
    """打印横幅"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")


def main():
    print_banner("🚀 BioLitKG 大规模分析测试")
    
    # ========== 配置参数 ==========
    
    # 搜索配置
    TOPIC = "single cell RNA sequencing"  # 核心主题(简洁!)
    MAX_SEARCH = 500     # 搜索数量(广撒网)
    MAX_ANALYZE = 150    # 分析数量(深度分析)
    YEAR_FROM = 2015     # 起始年份
    YEAR_TO = 2024       # 结束年份
    
    # 功能开关
    ENRICH_CITATIONS = True   # 补充引用数(推荐开启)
    USE_ARXIV = True          # 使用arXiv
    USE_PUBMED = True         # 使用PubMed
    USE_LLM = True            # AI分析
    CREATE_VIZ = True         # 生成可视化
    
    # 输出配置
    OUTPUT_NAME = f"scrna_large_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    OUTPUT_DIR = Path(f"outputs/{OUTPUT_NAME}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 显示配置
    print("📋 分析配置:")
    print(f"  主题: {TOPIC}")
    print(f"  搜索数量: {MAX_SEARCH} 篇")
    print(f"  分析数量: {MAX_ANALYZE} 篇")
    print(f"  补充引用数: {'是' if ENRICH_CITATIONS else '否'}")
    print(f"  年份范围: {YEAR_FROM}-{YEAR_TO}")
    print(f"  数据源: {'arXiv' if USE_ARXIV else ''}{', ' if USE_ARXIV and USE_PUBMED else ''}{'PubMed' if USE_PUBMED else ''}")
    print(f"  AI分析: {'启用' if USE_LLM else '禁用'}")
    print(f"  可视化: {'生成' if CREATE_VIZ else '不生成'}")
    print(f"  输出位置: {OUTPUT_DIR}")
    print()
    
    # 检查API密钥
    if USE_LLM and not os.getenv('LLM_API_KEY'):
        print("❌ 错误: 未设置 LLM_API_KEY 环境变量")
        print("   请先运行: export LLM_API_KEY='your-key'")
        sys.exit(1)
    
    try:
        # ========== 步骤1: 搜索文献 ==========
        print_banner("步骤1/5: 搜索文献")
        
        print(f"🔍 搜索关键词: {TOPIC}")
        print(f"📚 目标数量: {MAX_SEARCH} 篇")
        print(f"⏱️  预计时间: 1-2分钟")
        print()
        
        # 配置数据源
        sources = []
        if USE_ARXIV:
            sources.append("arxiv")
        if USE_PUBMED:
            sources.append("pubmed")
        
        if not sources:
            print("❌ 错误: 至少需要选择一个数据源")
            sys.exit(1)
        
        search = UnifiedLiteratureSearch()
        
        # 执行搜索
        # max_results_per_source: 每个数据源返回的结果数
        # 有2个数据源(arXiv+PubMed),所以设置为MAX_SEARCH//2让总数接近目标
        papers = search.search(
            query=TOPIC,
            max_results_per_source=MAX_SEARCH // 2,  # 每个源250篇
            total_max_results=MAX_SEARCH  # 总共最多500篇
        )
        
        print(f"✓ 搜索完成: 找到 {len(papers)} 篇论文")
        
        if not papers:
            print("❌ 没有找到论文,请检查网络连接或调整搜索关键词")
            sys.exit(1)
        
        # ========== 步骤2: 按年份筛选 ==========
        print_banner("步骤2/5: 筛选论文")
        
        print(f"📅 年份筛选: {YEAR_FROM}-{YEAR_TO}")
        papers = [p for p in papers if p.year and YEAR_FROM <= p.year <= YEAR_TO]
        print(f"✓ 年份筛选后: {len(papers)} 篇")
        
        if not papers:
            print(f"❌ 筛选后没有论文,请调整年份范围")
            sys.exit(1)
        
        # ========== 步骤3: 补充引用数 ==========
        if ENRICH_CITATIONS:
            print_banner("步骤3/5: 补充引用数")
            
            print(f"📊 使用 Semantic Scholar 补充引用数")
            print(f"📚 需要处理: {len(papers)} 篇")
            print(f"⏱️  预计时间: {len(papers) // 50 + 1}-{len(papers) // 30 + 2} 分钟")
            print()
            
            try:
                enricher = CitationEnricher()
                papers = enricher.enrich_citations(papers, show_progress=True)
                
                # 统计
                with_citations = sum(1 for p in papers if p.citation_count and p.citation_count > 0)
                print(f"\n✓ 引用数补充完成: {with_citations}/{len(papers)} 篇有引用数据")
                
                # 按引用数排序
                papers = sorted(papers, key=lambda p: p.citation_count or 0, reverse=True)
                print(f"✓ 已按引用数降序排序")
                
            except ImportError:
                print("⚠️  semanticscholar 包未安装,跳过引用数补充")
                print("   安装: pip install semanticscholar")
                # 按年份排序
                papers = sorted(papers, key=lambda p: p.year or 0, reverse=True)
            except Exception as e:
                print(f"⚠️  引用数补充失败: {e}")
                papers = sorted(papers, key=lambda p: p.year or 0, reverse=True)
        else:
            print_banner("步骤3/5: 跳过引用数补充")
            # 按年份排序
            papers = sorted(papers, key=lambda p: p.year or 0, reverse=True)
            print(f"✓ 已按年份降序排序")
        
        # 限制数量
        papers = papers[:MAX_ANALYZE]
        print(f"\n✓ 最终选择: {len(papers)} 篇论文进行分析")
        
        # 显示Top 5
        print(f"\n📊 Top 5 论文:")
        for i, p in enumerate(papers[:5], 1):
            cit = p.citation_count or 0
            year = p.year or '?'
            print(f"  {i}. [{cit:4d}引, {year}年] {p.title[:65]}...")
        
        # ========== 步骤4: 分析工作流程 ==========
        print_banner("步骤4/5: 分析工作流程")
        
        print(f"🤖 AI分析: {'启用' if USE_LLM else '禁用'}")
        print(f"📚 分析论文: {len(papers)} 篇")
        print(f"⏱️  预计时间: {2 + len(papers) // 50} 分钟")
        print()
        
        analyzer = WorkflowAnalyzer(
            use_llm=USE_LLM,
            max_papers=MAX_ANALYZE,
            year_from=YEAR_FROM,
            year_to=YEAR_TO
        )
        
        result = analyzer.analyze_workflow(papers)
        
        print(f"✓ 识别步骤: {len(result['steps'])} 个")
        print(f"✓ 识别工具: {len(result['tools'])} 个")
        
        # ========== 步骤5: 生成报告和可视化 ==========
        print_banner("步骤5/5: 生成报告和可视化")
        
        # 生成报告
        report_file = OUTPUT_DIR / "WORKFLOW_REPORT.md"
        analyzer.generate_workflow_report(result, output_path=report_file)
        print(f"✓ 报告已保存: {report_file}")
        
        # 生成论文清单 (简化版)
        papers_list_file = OUTPUT_DIR / "papers_list.md"
        papers_list_content = "# 论文清单\n\n"
        papers_list_content += f"共 {len(papers)} 篇论文\n\n"
        for i, paper in enumerate(papers, 1):
            # 处理作者名称 (支持字符串或Author对象)
            if paper.authors:
                author_names = []
                for a in paper.authors[:3]:
                    if isinstance(a, str):
                        author_names.append(a)
                    else:
                        # Author对象,尝试多个属性
                        name = getattr(a, 'name', None) or getattr(a, 'full_name', None) or str(a)
                        author_names.append(name)
                authors_str = ', '.join(author_names)
                if len(paper.authors) > 3:
                    authors_str += ' 等'
            else:
                authors_str = "未知"
            
            papers_list_content += f"{i}. **{paper.title}**\n"
            papers_list_content += f"   - 作者: {authors_str}\n"
            papers_list_content += f"   - 年份: {paper.year}\n"
            papers_list_content += f"   - 引用数: {paper.citation_count or 0}\n"
            if paper.doi:
                papers_list_content += f"   - DOI: [{paper.doi}](https://doi.org/{paper.doi})\n"
            if paper.arxiv_id:
                papers_list_content += f"   - arXiv: [{paper.arxiv_id}](https://arxiv.org/abs/{paper.arxiv_id})\n"
            if paper.pubmed_id:
                papers_list_content += f"   - PubMed: [PMID:{paper.pubmed_id}](https://pubmed.ncbi.nlm.nih.gov/{paper.pubmed_id}/)\n"
            papers_list_content += "\n"
        
        papers_list_file.write_text(papers_list_content, encoding='utf-8')
        print(f"✓ 论文清单已保存: {papers_list_file}")
        
        # 生成可视化
        if CREATE_VIZ:
            print(f"\n📊 生成可视化...")
            
            visualizer = WorkflowVisualizer()
            
            # 知识图谱网络
            network_file = OUTPUT_DIR / "workflow_network.html"
            visualizer.create_workflow_network(
                workflow_result=result,
                papers=papers,
                output_path=str(network_file)
            )
            print(f"✓ 网络图已保存: {network_file}")
            
            # 统计图表
            stats_file = OUTPUT_DIR / "paper_statistics.html"
            visualizer.create_paper_statistics(
                papers=papers,
                output_path=str(stats_file)
            )
            print(f"✓ 统计图已保存: {stats_file}")
        
        # ========== 完成 ==========
        print_banner("✅ 分析完成!")
        
        print("📂 输出文件:")
        print(f"  📄 {report_file}")
        print(f"  📄 {papers_list_file}")
        if CREATE_VIZ:
            print(f"  🌐 {OUTPUT_DIR / 'workflow_network.html'}")
            print(f"  📊 {OUTPUT_DIR / 'paper_statistics.html'}")
        
        print(f"\n💡 查看可视化:")
        print(f"  open {OUTPUT_DIR / 'workflow_network.html'}")
        print(f"  open {OUTPUT_DIR / 'paper_statistics.html'}")
        
        print(f"\n📊 分析统计:")
        print(f"  搜索论文: {MAX_SEARCH} 篇")
        print(f"  分析论文: {len(papers)} 篇")
        print(f"  识别步骤: {len(result['steps'])} 个")
        print(f"  识别工具: {len(result['tools'])} 个")
        
        if ENRICH_CITATIONS:
            with_cit = sum(1 for p in papers if p.citation_count and p.citation_count > 0)
            avg_cit = sum(p.citation_count or 0 for p in papers) / len(papers)
            print(f"  引用数据: {with_cit}/{len(papers)} 篇")
            print(f"  平均引用: {avg_cit:.1f} 次")
        
        print("\n🎉 成功!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

