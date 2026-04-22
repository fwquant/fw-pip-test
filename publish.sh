#!/bin/bash
set -eo pipefail

# ===================== 自动赋权 =====================
if [ ! -x "$0" ]; then
    echo "🔑 自动赋予执行权限..."
    chmod +x "$0"
    exec "$0" "$@"
fi

# ===================== 加载 .env =====================
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ 错误：.env 文件不存在！"
    exit 1
fi

# ===================== 【动态读取 setup.py 配置】=====================
# 自动读取包名
PACKAGE_NAME=$(python3 -c "
import ast
with open('setup.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if hasattr(target, 'id') and target.id == 'PIP包名':
                print(node.value.value)
                exit()
print('fw_pip')
")

# 自动读取当前本地版本
LOCAL_VERSION=$(python3 -c "
import ast
with open('setup.py', 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if hasattr(target, 'id') and target.id == '版本号':
                print(node.value.value)
                exit()
print('1.0.0')
")

# ===================== 基础配置 =====================
PYPI_TOKEN="$PYPI_API_TOKEN"
DEBUG_MODE=0

# ===================== 参数解析 =====================
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--debug) DEBUG_MODE=1; shift ;;
        *) echo "⚠️ 未知参数：$1，仅支持 -d/--debug"; shift ;;
    esac
done

# ===================== 关键校验 =====================
if [ -z "$PYPI_TOKEN" ]; then
    echo "❌ 错误：PYPI_API_TOKEN 未配置，请检查 .env"
    exit 1
fi

if [ ! -f "setup.py" ]; then
    echo "❌ 错误：当前目录未找到 setup.py"
    exit 1
fi

echo "📦 动态读取包名：$PACKAGE_NAME"
echo "🏷️  本地当前版本：$LOCAL_VERSION"

# ===================== 获取 PyPI 最新版本 =====================
echo "🔍 获取 PyPI 最新版本..."

LATEST=$(curl -s --connect-timeout 10 --max-time 15 "https://pypi.org/pypi/$PACKAGE_NAME/json" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    versions = sorted(data['releases'].keys(), key=lambda x: tuple(map(int, x.split('.'))))
    print(versions[-1] if versions else '1.0.0')
except:
    print('1.0.0')
")

echo "📌 PyPI 最新版本：$LATEST"

# ===================== 自动版本 +1 =====================
IFS=. read major minor patch <<< "$LATEST"
NEW_PATCH=$((patch + 1))
NEW_VERSION="$major.$minor.$NEW_PATCH"

echo "✅ 即将发布新版本：$NEW_VERSION"

# ===================== 自动写入新版本到 setup.py =====================
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^版本号 = \".*\"/版本号 = \"$NEW_VERSION\"/" setup.py
else
    sed -i "s/^版本号 = \".*\"/版本号 = \"$NEW_VERSION\"/" setup.py
fi

# ===================== 清理函数 =====================
cleanup() {
    echo "🗑️ 清理打包文件..."
    rm -rf dist/ build/ *.egg-info
}

# ===================== 打包 =====================
echo "🔴 清理历史文件..."
cleanup

echo "🟡 开始打包 $PACKAGE_NAME $NEW_VERSION..."
if [ $DEBUG_MODE -eq 1 ]; then
    python setup.py sdist bdist_wheel
else
    python setup.py sdist bdist_wheel >/dev/null 2>&1
fi

# 打包校验
if [ -z "$(ls dist/*.whl dist/*.tar.gz 2>/dev/null)" ]; then
    echo "❌ 打包失败：未生成任何发布文件"
    cleanup
    exit 1
fi

# ===================== 上传 =====================
echo "🟢 上传到 PyPI..."
if [ $DEBUG_MODE -eq 1 ]; then
    twine upload --username __token__ --password "$PYPI_TOKEN" dist/* --verbose
else
    twine upload --username __token__ --password "$PYPI_TOKEN" dist/*
fi

# ===================== 收尾 =====================
if [ $DEBUG_MODE -ne 1 ]; then
    cleanup
fi

echo ""
echo "🎉 发布成功！"
echo "📦 新版本：$NEW_VERSION"
echo "🔧 安装：pip install $PACKAGE_NAME"
echo "🔧 卸载：pip uninstall -y $PACKAGE_NAME"
echo "🔍 查看:pip show $PACKAGE_NAME"
