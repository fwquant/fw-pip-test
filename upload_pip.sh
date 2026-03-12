#!/bin/bash

# ===================== 自动赋权逻辑 =====================
# 检测当前脚本是否有执行权限，若无则自动赋权并重新执行
if [ ! -x "$0" ]; then
    echo "🔑 脚本无执行权限，自动赋予..."
    chmod +x "$0"
    # 重新执行当前脚本（执行后退出原进程）
    exec "$0" "$@"
fi

if [ -f ".env" ]; then
  # 读取 .env 文件，将每一行的 KEY=VALUE 加载到当前Shell环境
  export $(grep -v '^#' .env | xargs)
else
  echo "错误：.env 文件不存在！请先创建 .env 并配置 PYPI_API_TOKEN"
  exit 1
fi


# ===================== 配置项（按需修改）=====================
# 包名（对应 PyPI 上的包名，如 sgg-test、fw-pip-test）
# 方式1：默认取脚本父目录名作为包名（动态）
# 脚本路径：/Users/yanhuang/github/fwquant/fw-pip-test/upload_pip.sh
# 父目录名：fw-pip-test（自动提取）
SCRIPT_PATH=$(realpath "$0")          # 获取脚本绝对路径
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")  # 获取脚本所在目录路径
DEFAULT_PACKAGE_NAME=$(basename "$SCRIPT_DIR")  # 提取目录名作为默认包名
# 方式2：支持手动指定（注释掉下面这行则使用动态包名，取消注释则手动指定）
# DEFAULT_PACKAGE_NAME="fw-pip-test"
# 最终包名（优先级：手动指定 > 动态目录名）
PACKAGE_NAME="${DEFAULT_PACKAGE_NAME}"

# PyPI API Token（你的令牌）
PYPI_TOKEN=$PYPI_API_TOKEN
# ============================================================

# ===================== 参数解析逻辑 =====================
# 默认关闭调试模式
DEBUG_MODE=0

# 解析命令行参数（支持 -d/--debug 开启调试模式）
while [[ $# -gt 0 ]]; do
    case "$1" in
        -d|--debug)
            DEBUG_MODE=1
            shift  # 跳过参数名
            ;;
        *)
            # 未知参数提示
            echo "⚠️  未知参数：$1，仅支持 -d/--debug 开启调试模式"
            shift
            ;;
    esac
done

# 根据调试模式设置 twine 参数
if [ $DEBUG_MODE -eq 1 ]; then
    TWINE_ARGS="--username __token__ --password \"${PYPI_TOKEN}\" dist/* --verbose"
    echo "🔍 调试模式已开启，将输出详细日志..."
else
    TWINE_ARGS="--username __token__ --password \"${PYPI_TOKEN}\" dist/*"
fi

# 关键修正：将包名中的 - 转为 _，匹配 egg-info 目录名
EGG_INFO_NAME="${PACKAGE_NAME//-/_}.egg-info"

# 定义清理函数（成功/失败均执行）
cleanup() {
    echo "🗑️ 清理打包文件（dist/build/${EGG_INFO_NAME}）..."
    rm -rf dist/ build/ "${EGG_INFO_NAME}"
}

# 第一步：删除旧打包资料（打包前清理）
echo "🔴 清理旧打包文件..."
cleanup

# 第二步：打包（sdist 源码包 + bdist_wheel 轮子包）
echo "🟡 开始打包 ${PACKAGE_NAME}..."
# 调试模式下打印打包命令详情
if [ $DEBUG_MODE -eq 1 ]; then
    python setup.py sdist bdist_wheel
else
    # 非调试模式仅输出关键错误
    python setup.py sdist bdist_wheel > /dev/null 2>&1
fi

if [ $? -ne 0 ]; then  # 检查打包是否失败
    echo "❌ 打包失败！请检查 setup.py 或依赖是否正确"
    # 调试模式下不清理（方便排查打包产物问题），非调试模式清理
    if [ $DEBUG_MODE -ne 1 ]; then
        cleanup
    fi
    exit 1
fi

# 第三步：带 Token 自动上传到 PyPI
echo "🟢 开始上传 ${PACKAGE_NAME} 到 PyPI..."
# 执行 twine 上传（根据模式决定是否详细输出）
eval "twine upload ${TWINE_ARGS}"
UPLOAD_RESULT=$?  # 保存上传结果

# 第四步：根据调试模式决定是否清理打包文件
if [ $DEBUG_MODE -eq 1 ]; then
    echo "🔍 调试模式下保留打包文件，方便排查问题：$(pwd)/dist"
else
    cleanup
fi

# 根据上传结果输出提示
if [ $UPLOAD_RESULT -eq 0 ]; then
    echo "✅ 上传成功！"
    if [ $DEBUG_MODE -eq 1 ]; then
        echo "📌 调试模式 - 打包文件未清理：$(pwd)/dist"
    else
        echo "📌 安装/更新命令：pip install --upgrade ${PACKAGE_NAME} --index-url https://pypi.org/simple/"
    fi
else
    echo "❌ 上传失败！"
    if [ $DEBUG_MODE -eq 1 ]; then
        echo "📌 调试模式 - 打包文件未清理，请检查 dist 目录和详细日志"
    else
        echo "📌 建议使用 --debug 模式重新执行，查看详细错误信息"
    fi
    exit 1
fi