#!/bin/bash
set -e

# 自动赋权
if [ ! -x "$0" ]; then
    echo "🔑 自动赋予执行权限..."
    chmod +x "$0"
    exec "$0" "$@"
fi

# 加载 .env
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ 错误：.env 文件不存在！"
    exit 1
fi

# ===================== 配置 =====================
PACKAGE_NAME="fw-pip-test"
PYPI_TOKEN="$PYPI_API_TOKEN"
DEBUG_MODE=0
# =================================================

# 参数解析
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--debug) DEBUG_MODE=1; shift ;;
        *) echo "⚠️ 未知参数 $1"; shift ;;
    esac
done

# ===================== 自动获取最新版本号 =====================
echo "🔍 获取 PyPI 最新版本..."

LATEST=$(curl -s "https://pypi.org/pypi/$PACKAGE_NAME/json" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    versions = list(data['releases'].keys())
    versions.sort(key=lambda v: list(map(int, v.split('.'))))
    print(versions[-1])
except:
    print('1.0.0')
")

echo "📌 PyPI 最新版本：$LATEST"

# 自动 +1
IFS=. read major minor patch <<< "$LATEST"
NEW_PATCH=$((patch + 1))
NEW_VERSION="$major.$minor.$NEW_PATCH"
echo "✅ 即将发布：$NEW_VERSION"

# 写入 setup.py
sed -i '' "s/^VERSION = \".*\"/VERSION = \"$NEW_VERSION\"/" setup.py

# ===================== 打包上传 =====================
cleanup() {
    echo "🗑️ 清理打包文件..."
    rm -rf dist/ build/ *.egg-info
}

echo "🔴 清理..."
cleanup

echo "🟡 打包中..."
if [ $DEBUG_MODE -eq 1 ]; then
    python setup.py sdist bdist_wheel
else
    python setup.py sdist bdist_wheel > /dev/null 2>&1
fi

echo "🟢 上传到 PyPI..."
if [ $DEBUG_MODE -eq 1 ]; then
    twine upload --username __token__ --password "$PYPI_TOKEN" dist/* --verbose
else
    twine upload --username __token__ --password "$PYPI_TOKEN" dist/*
fi

# 清理
if [ $DEBUG_MODE -ne 1 ]; then
    cleanup
fi

echo "🎉 发布成功！新版本：$NEW_VERSION"
echo "📦 安装：pip install --upgrade $PACKAGE_NAME"