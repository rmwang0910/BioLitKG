"""工具模块"""
from .text_processor import TextProcessor

try:
    from .citation_enricher import CitationEnricher
    __all__ = ['TextProcessor', 'CitationEnricher']
except ImportError:
    __all__ = ['TextProcessor']

