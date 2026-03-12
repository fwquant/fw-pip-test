import requests
from packaging.version import Version

# 你的基础配置
PACKAGE_NAME = "fw-pip-test"  # PyPI 包名
BASE_VERSION = "1.0"  # 主版本号（固定为1.0，只更新小版本）

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

# ===================== 使用示例 =====================
if __name__ == "__main__":
    # 自动获取下一个版本号
    VERSION = get_next_patch_version(PACKAGE_NAME, BASE_VERSION)
    print(f"最终使用版本号：{VERSION}")

    # 输出示例（假设当前最新是 1.0.11）：
    # 当前最新版本：1.0.11 → 下一个版本：1.0.12
    # 最终使用版本号：1.0.12