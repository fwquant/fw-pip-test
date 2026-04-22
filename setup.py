import os
from setuptools import setup, find_packages

# ===================== 核心：版本号会被 publish.sh 自动更新 =====================
版本号 = "1.0.17"
PIP包名 = "fw_pip"
一句话描述 = "fuwenquant 的一个PYPI测试包（包含add_one和helloworld函数）"


# ==============================================================================

def 获得详细描述():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else f"{一句话描述}"
    return f"{一句话描述}"


setup(
    name=PIP包名,
    version=版本号,  # 这里不变
    description=一句话描述,
    author="fwquant",
    author_email="fuwenquant@gmail.com",
    long_description=获得详细描述(),
    long_description_content_type="text/markdown",
    license="MIT",

    url="",
    packages=find_packages(),  # 这里简化，自动找所有包
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "six>=1.10.0",
    ],
    keywords=["bin", "test", "demo", "add_one"],
    include_package_data=True,
    zip_safe=False,
)
