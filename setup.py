import os  # 导入os模块，用于文件路径和存在性检查（容错处理）

import requests
from packaging.version import Version
from setuptools import setup, find_packages  # 导入setuptools核心打包函数


def get_next_patch_version(package_name: str, base_version: str = "1.0") -> str:
    """
    查询 PyPI 上指定包的最新版本，自动计算下一个小版本号
    :param package_name: PyPI 包名（如 fw-pip-test）
    :param base_version: 主版本号（如 "1.0"）
    :return: 拼接后的新版本号（如 "1.0.12"）
    """
    # PyPI 的 API 地址（查询包的所有版本）
    pypi_api_url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        # 发送请求获取包的版本信息
        response = requests.get(pypi_api_url, timeout=10)

        # 情况1：包未发布（首次发布）
        if response.status_code == 404:
            print(f"包 {package_name} 未在 PyPI 发布，使用初始版本 {base_version}.0")
            return f"{base_version}.0"

        # 确保请求成功
        response.raise_for_status()
        data = response.json()

        # 提取所有版本号并过滤出符合 base_version 的版本
        all_versions = list(data["releases"].keys())
        valid_versions = []

        for ver_str in all_versions:
            try:
                ver = Version(ver_str)
                # 只匹配主版本号一致的版本（如 1.0.x）
                if f"{ver.major}.{ver.minor}" == base_version:
                    valid_versions.append(ver)
            except ValueError:
                # 跳过非标准版本号（如 1.0.10-beta）
                continue

        # 情况2：有符合规则的版本，取最新的小版本号 +1
        if valid_versions:
            latest_ver = max(valid_versions)
            latest_patch = latest_ver.micro  # 提取小版本号（如 1.0.11 → 11）
            next_patch = latest_patch + 1
            next_version = f"{base_version}.{next_patch}"
            print(f"当前最新版本：{latest_ver} → 下一个版本：{next_version}")
            return next_version

        # 情况3：无符合规则的版本（如只有 1.1.x，没有 1.0.x）
        else:
            print(f"未找到 {base_version}.x 版本，使用初始版本 {base_version}.0")
            return f"{base_version}.0"

    except requests.exceptions.RequestException as e:
        # 网络异常时的降级处理
        print(f"查询 PyPI 失败（{e}），请检查网络或手动指定版本")
        raise  # 也可以改为返回默认值，如 return f"{base_version}.0"


# 核心配置常量（统一管理，便于修改）
PACKAGE_NAME = "fw-pip-test"  # 包名（PyPI全网唯一，测试包加-test后缀）
VERSION = get_next_patch_version(package_name=PACKAGE_NAME, base_version="1.0")  # 版本号（语义化版本，首次发布用1.0.0）
AUTHOR = "fwquant"  # 作者名（建议与PyPI注册账号一致）
AUTHOR_EMAIL = "fuwenquant@gmail.com"  # 作者邮箱（必须与PyPI注册邮箱一致）
SHORT_DESCRIPTION = "fuwenquant 的第一个测试包（包含add_one和helloworld函数）"  # 包简短描述（<100字符）


# 新增：README读取容错（空文件/不存在都不报错）
def get_long_description():  # 定义README读取函数，核心作用是容错
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")  # 拼接README文件的绝对路径
    if os.path.exists(readme_path):  # 检查README文件是否存在
        with open(readme_path, "r", encoding="utf-8") as f:  # 以UTF-8编码打开README文件
            content = f.read().strip()  # 读取文件内容并去除首尾空白字符
            # 若README为空，返回简短描述，否则返回README内容
            return content if content else SHORT_DESCRIPTION
    return SHORT_DESCRIPTION  # 无README文件时，返回简短描述


setup(
    name=PACKAGE_NAME,  # 指定包名（必填，与常量保持一致）
    version=VERSION,  # 指定包版本（必填，语义化版本不可重复）
    author=AUTHOR,  # 指定作者名（必填，显示在PyPI包页面）
    author_email=AUTHOR_EMAIL,  # 指定作者邮箱（必填，PyPI身份验证用）
    description=SHORT_DESCRIPTION,  # 指定包简短描述（必填，PyPI搜索结果展示）
    license="MIT",  # 指定开源协议（修正：小写l，MIT为最宽松协议）
    long_description=get_long_description(),  # 指定包详细描述（容错读取README）
    long_description_content_type="text/markdown",  # 指定详细描述格式为Markdown
    url="",  # 包源码地址（无GitHub则留空）
    packages=find_packages(include=["bin", "tests"]),  # 递归查找fw-pip包及其子包
    classifiers=[  # 包分类标签（帮助PyPI索引，提升可发现性）
        "Development Status :: 3 - Alpha",  # 开发状态：测试版（Alpha）
        "Intended Audience :: Developers",  # 目标用户：开发者
        "Programming Language :: Python :: 3",  # 支持Python3
        "Programming Language :: Python :: 3.8",  # 支持Python3.8
        "Programming Language :: Python :: 3.9",  # 支持Python3.9
        "Programming Language :: Python :: 3.10",  # 支持Python3.10
        "License :: OSI Approved :: MIT License",  # 开源协议：MIT
        "Operating System :: OS Independent",  # 支持所有操作系统
    ],
    python_requires=">=3.8",  # 限制Python最低版本为3.8
    install_requires=[  # 包依赖列表（用户安装时自动下载）
        "six>=1.10.0",  # 仅11KB，Python2/3兼容工具，几乎无安装耗时
    ],
    keywords=["bin", "test", "demo", "add_one"],  # 搜索关键词，提升PyPI搜索曝光
    include_package_data=True,  # 包含非代码文件（如README）
    zip_safe=False,  # 禁止压缩包，避免文件读取异常
)

# ===================== 使用示例 =====================
if __name__ == "__main__":
    # 自动获取下一个版本号
    VERSION = get_next_patch_version(package_name=PACKAGE_NAME)
    print(f"最终使用版本号：{VERSION}")

    # 输出示例（假设当前最新是 1.0.11）：
    # 当前最新版本：1.0.11 → 下一个版本：1.0.12
    # 最终使用版本号：1.0.12
