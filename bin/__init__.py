# 导出核心功能，用户导入时可直接
from bin.core import *

__version__ = "1.0.0"  # 包的版本号

if __name__ == '__main__':
    result = add_one(10)
    print(f"result: {result}")
