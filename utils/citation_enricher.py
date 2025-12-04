"""
引用数补充工具

使用Semantic Scholar API为论文补充引用数,但不用于搜索
"""
import logging
import time
from typing import List, Optional

try:
    from semanticscholar import SemanticScholar
    HAS_S2 = True
except ImportError:
    HAS_S2 = False

from literature.base_client import PaperMetadata

logger = logging.getLogger(__name__)


class CitationEnricher:
    """
    引用数补充器
    
    使用Semantic Scholar API为论文补充引用数,但不用于搜索
    这样既保持搜索速度快,又能获得引用统计
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            api_key: Semantic Scholar API密钥(可选,无密钥时有速率限制)
        """
        if not HAS_S2:
            raise ImportError(
                "需要安装semanticscholar包:\n"
                "pip install semanticscholar"
            )
        
        self.s2 = SemanticScholar(api_key=api_key)
        self.api_key = api_key
        
        # 速率限制
        self.request_interval = 0.1 if api_key else 1.0  # 有key时更快
        self.last_request_time = 0
        
        logger.info("CitationEnricher initialized")
    
    def enrich_citations(
        self,
        papers: List[PaperMetadata],
        show_progress: bool = True
    ) -> List[PaperMetadata]:
        """
        为论文列表补充引用数
        
        Args:
            papers: 论文列表
            show_progress: 是否显示进度
            
        Returns:
            补充了引用数的论文列表
        """
        if not papers:
            return papers
        
        enriched_count = 0
        failed_count = 0
        
        if show_progress:
            print(f"\n📊 补充引用数...")
            print(f"  总论文数: {len(papers)}")
            print(f"  正在查询Semantic Scholar API...")
        
        for i, paper in enumerate(papers, 1):
            # 速率限制
            self._rate_limit()
            
            # 尝试通过不同ID查询
            s2_paper = None
            
            # 1. 优先用DOI
            if paper.doi and not s2_paper:
                s2_paper = self._get_paper_safe(f"DOI:{paper.doi}")
            
            # 2. 尝试arXiv ID
            if paper.arxiv_id and not s2_paper:
                s2_paper = self._get_paper_safe(f"ARXIV:{paper.arxiv_id}")
            
            # 3. 尝试PubMed ID
            if paper.pubmed_id and not s2_paper:
                s2_paper = self._get_paper_safe(f"PMID:{paper.pubmed_id}")
            
            # 4. 尝试标题搜索(最后手段)
            if not s2_paper and paper.title:
                s2_paper = self._search_by_title(paper.title)
            
            # 更新引用数
            if s2_paper:
                paper.citation_count = getattr(s2_paper, 'citationCount', 0) or 0
                enriched_count += 1
                
                # 也可以补充其他信息
                if not paper.doi and hasattr(s2_paper, 'externalIds'):
                    ext_ids = s2_paper.externalIds or {}
                    if 'DOI' in ext_ids:
                        paper.doi = ext_ids['DOI']
                
                if show_progress and i % 10 == 0:
                    print(f"  进度: {i}/{len(papers)} ({enriched_count}篇成功)")
            else:
                failed_count += 1
                paper.citation_count = 0  # 未找到的设为0
        
        if show_progress:
            print(f"\n✓ 补充完成!")
            print(f"  成功: {enriched_count}/{len(papers)} 篇")
            print(f"  失败: {failed_count} 篇")
            
            # 显示引用数统计
            citations = [p.citation_count for p in papers if p.citation_count]
            if citations:
                print(f"\n📈 引用数统计:")
                print(f"  平均: {sum(citations)/len(citations):.1f}")
                print(f"  最高: {max(citations)}")
                print(f"  中位数: {sorted(citations)[len(citations)//2]}")
        
        return papers
    
    def _get_paper_safe(self, paper_id: str) -> Optional[any]:
        """安全地获取论文(带异常处理)"""
        try:
            return self.s2.get_paper(paper_id)
        except Exception as e:
            logger.debug(f"Failed to get paper {paper_id}: {e}")
            return None
    
    def _search_by_title(self, title: str) -> Optional[any]:
        """通过标题搜索(最后手段)"""
        try:
            results = self.s2.search_paper(title, limit=1)
            if results and len(results) > 0:
                # 检查标题相似度
                result = results[0]
                if hasattr(result, 'title'):
                    # 简单相似度检查
                    if title.lower()[:50] in result.title.lower() or result.title.lower()[:50] in title.lower():
                        return result
            return None
        except Exception as e:
            logger.debug(f"Failed to search by title: {e}")
            return None
    
    def _rate_limit(self):
        """速率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        
        self.last_request_time = time.time()

