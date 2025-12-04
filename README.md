# 🧬 BioLitKG

**Bioinformatics Literature Knowledge Graph**

> 生物医学文献知识图谱与工作流程分析工具

[中文文档](#中文文档) • [Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation)

---

## Features

### 🔍 Smart Literature Search
- arXiv + PubMed dual-source integration
- Semantic Scholar citation enrichment
- Customizable filtering (year, citations, keywords)

### 📊 Workflow Analysis  
- Automatic extraction of analysis steps
- Tool identification and ranking
- AI-generated best practices

### 🕸️ Knowledge Graph Visualization
- Interactive network graphs (steps-tools-papers)
- Statistical charts
- Tool comparison charts

### 🎛️ Full Parameter Control
- Literature count: `max_papers`
- Impact factor (citations): `min_citations`
- Year range: `year_from`, `year_to`
- Literature type: review/benchmark/protocol

### 🗣️ Interactive Mode
- **Chat-based parameter input**
- No code editing required
- User-friendly prompts

---

## Quick Start

### Installation

```bash
# Clone repository
cd BioLitKG

# One-click installation
./setup.sh
```

### Usage

```bash
# Set API key
export LLM_API_KEY='your-dashscope-api-key'

# Run interactive analysis
python analyze.py

# Follow the prompts to set:
# - Analysis topic
# - Paper count
# - Citation threshold
# - Year range
# - Output location
```

### Output

```
outputs/your_analysis/
├── WORKFLOW_REPORT.md          # Detailed report with citations
├── workflow_network.html       # Interactive knowledge graph
├── paper_statistics.html       # Statistical charts
├── tool_comparison.html        # Tool comparison
└── PAPERS_LIST.md              # Paper list with links
```

---

## 中文文档

### ⚡ 快速开始

```bash
# 1. 安装
./setup.sh

# 2. 设置密钥
export LLM_API_KEY='your-dashscope-api-key'

# 3. 运行交互式分析
python analyze.py
```

### 📊 生成内容

- 完整的工作流程报告(每个步骤都有文献引用)
- 交互式知识图谱网络(可拖拽、可缩放)
- 统计图表(年份分布、引用数分析)
- 工具使用频率对比
- 论文详细清单(DOI/arXiv/PubMed链接)

### 🎯 参数控制

通过对话设置:
- 文献数量 (20-500)
- 影响力筛选 (引用数 0-1000)
- 年份范围 (2010-2024)
- 文献类型 (review/benchmark/protocol)

### 📚 文档

- `START_HERE.md` - 快速开始指南
- `参数配置指南.md` - 完整参数说明

---

## Tech Stack

- **Literature Search**: arxiv, biopython, semanticscholar
- **LLM**: OpenAI-compatible API (Qwen, GPT, etc.)
- **Data Processing**: pandas, numpy, networkx
- **Visualization**: pyvis, plotly
- **Configuration**: pydantic

---

## Project Structure

```
BioLitKG/
├── analyze.py              # Interactive analysis script ⭐
├── literature/             # Literature search module
├── workflow/               # Workflow analysis & visualization
├── core/                   # LLM interface & configuration
├── models/                 # Data models
├── utils/                  # Utilities & citation enricher
├── outputs/                # Analysis results
└── docs/                   # Documentation
```

---

## Documentation

- **`START_HERE.md`** - Quick start guide
- **`参数配置指南.md`** - Parameter configuration (Chinese)
---

## Requirements

- Python >= 3.11
- See `requirements.txt` for dependencies

---

## Features

- ✅ Fully independent (no Kosmos dependency)
- ✅ Fast search (arXiv + PubMed)
- ✅ Citation enrichment (Semantic Scholar)
- ✅ Interactive mode (chat-based)
- ✅ Complete visualization
- ✅ Full parameter control
- ✅ Detailed citations in reports

---

## License

MIT License

---

## Acknowledgments

Built for bioinformatics literature analysis and workflow extraction.

---

<div align="center">

**Make bioinformatics literature analysis simple and efficient** 🚀

</div>
