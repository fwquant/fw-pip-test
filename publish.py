# -*- coding: utf-8 -*-
"""
PyPI 全自动发布脚本（全平台通用 Windows/Mac/Linux）
功能：自动版本+1、打包、上传、清理
"""
import os
import re
import sys
import json
import shutil
import subprocess
import requests
from dotenv import load_dotenv

# ===================== 加载环境变量 =====================
load_dotenv()


# ===================== 读取 setup.py 配置 =====================
def get_setup_value(key: str) -> str:
    with open("setup.py", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(rf'^{key}\s*=\s*"([^"]+)"', content, re.MULTILINE)
    return match.group(1) if match else ""


PACKAGE_NAME = get_setup_value("PIP包名")
LOCAL_VERSION = get_setup_value("版本号")

# ===================== 配置 =====================
PYPI_TOKEN = os.getenv("PYPI_API_TOKEN")
DEBUG_MODE = "--debug" in sys.argv or "-d" in sys.argv

# ===================== 校验 =====================
if not PYPI_TOKEN:
    print("❌ 错误：PYPI_API_TOKEN 未配置，请检查 .env")
    sys.exit(1)

if not os.path.exists("setup.py"):
    print("❌ 错误：未找到 setup.py")
    sys.exit(1)

print(f"📦 动态读取包名：{PACKAGE_NAME}")
print(f"🏷️  本地当前版本：{LOCAL_VERSION}")

# ===================== 获取 PyPI 最新版本 =====================
print("🔍 获取 PyPI 最新版本...")
LATEST_VERSION = "1.0.0"

try:
    url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        releases = list(data["releases"].keys())
        releases.sort(key=lambda x: tuple(map(int, x.split("."))))
        LATEST_VERSION = releases[-1] if releases else "1.0.0"
except:
    LATEST_VERSION = "1.0.0"

print(f"📌 PyPI 最新版本：{LATEST_VERSION}")

# ===================== 自动版本 +1 =====================
major, minor, patch = LATEST_VERSION.split(".")
new_patch = int(patch) + 1
NEW_VERSION = f"{major}.{minor}.{new_patch}"
print(f"✅ 即将发布新版本：{NEW_VERSION}")

# ===================== 写入 setup.py =====================
with open("setup.py", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r'^版本号 = ".*"', f'版本号 = "{NEW_VERSION}"', content, flags=re.MULTILINE)

with open("setup.py", "w", encoding="utf-8") as f:
    f.write(content)


# ===================== 清理 =====================
def clean():
    for folder in ["dist", "build", f"{PACKAGE_NAME}.egg-info"]:
        if os.path.exists(folder):
            shutil.rmtree(folder, ignore_errors=True)
    print("🗑️ 清理完成")


print("🔴 清理历史文件...")
clean()

# ===================== 打包 =====================
print(f"🟡 开始打包 {PACKAGE_NAME} {NEW_VERSION}...")
cmd = [sys.executable, "setup.py", "sdist", "bdist_wheel"]
if not DEBUG_MODE:
    subprocess.run(cmd, capture_output=True)
else:
    subprocess.run(cmd)

# 校验打包结果
if not os.path.exists("dist") or len(os.listdir("dist")) == 0:
    print("❌ 打包失败")
    clean()
    sys.exit(1)

# ===================== 上传 =====================
print("🟢 上传到 PyPI...")
upload_cmd = [
    "twine", "upload",
    "--username", "__token__",
    "--password", PYPI_TOKEN,
    "dist/*"
]
if DEBUG_MODE:
    upload_cmd.append("--verbose")

subprocess.run(upload_cmd, check=True)

# ===================== 收尾 =====================
if not DEBUG_MODE:
    clean()


print(f"📦 新版本：{NEW_VERSION}")
print(f"🔧 安装：pip install {PACKAGE_NAME}")
print(f"🔧 升级：pip install --upgrade {PACKAGE_NAME}")
print(f"🔍 查看:pip show {PACKAGE_NAME}")
print("\n🎉 发布成功！")
