#!/bin/bash
#
# 事件执行器插件 - 测试运行脚本
#
# 运行所有测试：单元测试 + 集成测试

set -e  # 遇到错误立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================="
echo "事件执行器插件 - 完整测试套件"
echo "======================================================================="
echo ""

# 检测 Python 版本
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "使用 Python 命令: $PYTHON_CMD"
echo ""

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================================
# 测试 1: 单元测试
# ============================================================
echo "======================================================================="
echo "测试 1/2: 单元测试 (test_unit.py)"
echo "======================================================================="
echo ""

if $PYTHON_CMD test_unit.py; then
    echo ""
    echo "✅ 单元测试通过"
    ((PASSED_TESTS++))
else
    echo ""
    echo "❌ 单元测试失败"
    ((FAILED_TESTS++))
fi

((TOTAL_TESTS++))
echo ""

# ============================================================
# 测试 2: 模拟事件测试（需要插件已安装）
# ============================================================
echo "======================================================================="
echo "测试 2/2: 模拟事件测试 (test_plugin.py)"
echo "======================================================================="
echo ""
echo "⚠️  注意: 此测试需要插件已安装到 MoviePilot 并配置完成"
echo "如果跳过此测试，请按 Ctrl+C"
echo ""
read -p "是否运行模拟事件测试? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if $PYTHON_CMD test_plugin.py; then
        echo ""
        echo "✅ 模拟事件测试通过"
        ((PASSED_TESTS++))
    else
        echo ""
        echo "❌ 模拟事件测试失败"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
else
    echo "⏭️  跳过模拟事件测试"
fi

echo ""

# ============================================================
# 测试总结
# ============================================================
echo "======================================================================="
echo "测试总结"
echo "======================================================================="
echo "总测试数: $TOTAL_TESTS"
echo "通过: $PASSED_TESTS"
echo "失败: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有测试通过！"
    echo ""
    echo "下一步:"
    echo "1. 将插件安装到 MoviePilot: cp -r eventexecutor /path/to/moviepilot/app/plugins/"
    echo "2. 在 MoviePilot 管理界面配置插件"
    echo "3. 运行集成测试验证功能"
    exit 0
else
    echo "⚠️  有 $FAILED_TESTS 个测试失败"
    echo "请检查上述错误信息并修复问题"
    exit 1
fi
