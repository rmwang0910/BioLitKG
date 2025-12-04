"""
文本处理工具
"""
import re
from typing import List, Set, Dict
from collections import Counter


class TextProcessor:
    """文本处理工具类"""
    
    # 生信领域常见实体模式
    GENE_PATTERNS = [
        r'\b[A-Z][A-Z0-9]{2,10}\b',  # 基因名 (e.g., TP53, BRCA1)
        r'\b[A-Z][a-z]{2,15}\d*\b'   # 基因名 (e.g., Gapdh, Actb)
    ]
    
    PROTEIN_PATTERNS = [
        r'\b[A-Z][a-z]+\s*\d+[a-z]?\b',  # 蛋白质 (e.g., Protein kinase 1)
    ]
    
    DISEASE_PATTERNS = [
        r'\b(?:cancer|carcinoma|disease|syndrome|disorder)\b',
    ]
    
    METHOD_KEYWORDS = [
        'sequencing', 'rna-seq', 'chip-seq', 'atac-seq', 'single-cell',
        'clustering', 'alignment', 'assembly', 'annotation', 'pipeline',
        'algorithm', 'workflow', 'analysis', 'method', 'approach',
        'scRNA-seq', 'bulk RNA-seq', 'GWAS', 'metagenomics'
    ]
    
    @staticmethod
    def extract_keywords(text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        # 简单的TF统计
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # 停用词
        stopwords = {
            'the', 'and', 'for', 'with', 'this', 'that', 'from',
            'are', 'was', 'were', 'been', 'have', 'has', 'had',
            'but', 'not', 'can', 'could', 'would', 'should'
        }
        
        words = [w for w in words if w not in stopwords]
        counter = Counter(words)
        return [word for word, _ in counter.most_common(top_k)]
    
    @staticmethod
    def extract_gene_mentions(text: str) -> Set[str]:
        """提取基因名称"""
        genes = set()
        for pattern in TextProcessor.GENE_PATTERNS:
            matches = re.findall(pattern, text)
            genes.update(matches)
        return genes
    
    @staticmethod
    def extract_method_mentions(text: str) -> Set[str]:
        """提取方法名称"""
        text_lower = text.lower()
        methods = set()
        for method in TextProcessor.METHOD_KEYWORDS:
            if method.lower() in text_lower:
                methods.add(method)
        return methods
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """计算文本相似度 (简单的Jaccard相似度)"""
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\-.,;:()]', '', text)
        return text.strip()
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """提取句子"""
        # 简单的句子分割
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

