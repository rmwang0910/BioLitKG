"""
BioLitKG - 生物医学文献知识图谱工具
"""
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name="bioliter-kg",
    version="1.0.0",
    author="BioLitKG Team",
    description="生物医学文献知识图谱与工作流程分析工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['tests', 'examples', 'outputs']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        'arxiv>=2.0.0',
        'biopython>=1.81',
        # 不使用Semantic Scholar
        # 'semanticscholar>=0.8.0',
        'openai>=1.0.0',
        'networkx>=3.1',
        'python-igraph>=0.11.0',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'pyvis>=0.3.2',
        'plotly>=5.17.0',
        'matplotlib>=3.7.0',
        'pydantic>=2.0.0',
        'pydantic-settings>=2.0.0',
        'python-dotenv>=1.0.0',
        'tqdm>=4.66.0',
        'requests>=2.31.0',
        'nltk>=3.8.1',
        'scikit-learn>=1.3.0',
    ],
    include_package_data=True,
    zip_safe=False,
)
