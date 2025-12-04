#!/bin/bash
# BioLitKG 一键完成脚本

echo "======================================================================"
echo "🧬 BioLitKG 一键完成安装"
echo "======================================================================"

# 检查conda环境
if [[ "$CONDA_DEFAULT_ENV" != "bioliter" ]]; then
    echo "⚠️  请先激活conda环境:"
    echo "   conda activate bioliter"
    exit 1
fi

echo ""
echo "📦 步骤1: 安装Python依赖包..."
echo "   - arxiv (arXiv文献搜索)"
echo "   - biopython (PubMed搜索)"
echo "   - 其他必要依赖..."

pip install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo "✓ Python依赖已安装"
else
    echo "❌ 依赖安装失败,请检查网络连接"
    exit 1
fi

echo ""
echo "🔧 步骤2: 安装BioLitKG..."
pip install -e . -q

if [ $? -eq 0 ]; then
    echo "✓ BioLitKG已安装"
else
    echo "❌ BioLitKG安装失败"
    exit 1
fi

echo ""
echo "🧪 步骤3: 测试导入..."
python -c "from workflow import WorkflowAnalyzer; from literature import UnifiedLiteratureSearch; print('✓ 所有模块导入成功!')"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "🎉 BioLitKG 安装完成!"
    echo "======================================================================"
    echo ""
    echo "📚 已启用的文献源:"
    echo "   ✅ arXiv - 计算机/物理/生物领域预印本"
    echo "   ✅ PubMed - 生物医学主要数据库"
    echo ""
    echo "🚀 下一步:"
    echo "   1. 设置API密钥:"
    echo "      export LLM_API_KEY='your-dashscope-api-key'"
    echo ""
    echo "   2. 运行单细胞分析示例:"
    echo "      python examples/scrna_workflow_analysis.py"
    echo ""
    echo "   3. 查看生成的报告:"
    echo "      ls outputs/scrna_analysis/"
    echo "      cat outputs/scrna_analysis/WORKFLOW_REPORT.md"
    echo ""
    echo "📖 查看文档:"
    echo "   - README.md - 完整功能介绍"
    echo "   - QUICK_START.md - 快速开始指南"
    echo ""
else
    echo ""
    echo "❌ 测试失败,请检查错误信息"
    exit 1
fi

