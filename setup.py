import os
from setuptools import setup, find_packages

# ===================== 核心：版本号会被 publish.sh 自动更新 =====================
VERSION = "1.0.16"
# ==============================================================================

def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content if content else "fuwenquant 的第一个测试包（包含add_one和helloworld函数）"
    return "fuwenquant 的第一个测试包（包含add_one和helloworld函数）"

setup(
    name="fw-pip-test",
    version=VERSION,          # 这里不变
    author="fwquant",
    author_email="fuwenquant@gmail.com",
    description="fuwenquant 的第一个测试包（包含add_one和helloworld函数）",
    license="MIT",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
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