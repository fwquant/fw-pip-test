import os  # 导入os模块，用于文件路径和存在性检查（容错处理）

from setuptools import setup, find_packages  # 导入setuptools核心打包函数

# 核心配置常量（统一管理，便于修改）
PACKAGE_NAME = "sgg-test"  # 包名（PyPI全网唯一，测试包加-test后缀）
VERSION = "1.0.3"  # 版本号（语义化版本，首次发布用1.0.0）
AUTHOR = "sgg-test"  # 作者名（建议与PyPI注册账号一致）
AUTHOR_EMAIL = "saogegood@163.com"  # 作者邮箱（必须与PyPI注册邮箱一致）
SHORT_DESCRIPTION = "saogegood的第一个测试包（包含add_one和helloworld函数）"  # 包简短描述（<100字符）


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
    packages=find_packages(include=["sgg", "tests"]),  # 递归查找sgg包及其子包
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
    keywords=["sgg", "test", "demo", "add_one"],  # 搜索关键词，提升PyPI搜索曝光
    include_package_data=True,  # 包含非代码文件（如README）
    zip_safe=False,  # 禁止压缩包，避免文件读取异常
)
