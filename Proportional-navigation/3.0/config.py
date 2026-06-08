# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-03 00:00:00
文件名: config.py
功能说明:比例导航法最小导航比搜索分析配置文件
版本号：3.0
"""

from pathlib import Path

# 当前实验根目录。
PROJECT_ROOT = Path(__file__).resolve().parent
# 当前实验输出根目录。
SAVE_DIR = PROJECT_ROOT / "outputs"
# 当前实验表格输出目录。
TABLE_DIR = SAVE_DIR / "tables"
# 当前实验图像输出目录。
FIGURE_DIR = SAVE_DIR / "figures"

SUMMARY_CSV = TABLE_DIR / "summary.csv"
SUMMARY_JSON = TABLE_DIR / "summary.json"
METRIC_PNG = FIGURE_DIR / "metrics.png"

TITLE = "实验 3.0：比例导航法最小导航比搜索"

DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 0.1
MAX_OVERLOAD_G = 20.0
CONVERGENCE_THRESHOLD_M = 2.0

TARGET_SPEED_MPS = 300.0
MISSILE_POSITION_M = (0.0, 0.0)
TARGET_POSITION_M = (10000.0, 3000.0)
TARGET_HEADING_DEG = 180.0
SPEED_RATIO_VALUES = [1.2, 1.4, 1.6, 1.8, 2.0, 2.2]
NAVIGATION_RATIO_SCAN = [x / 10.0 for x in range(10, 101)]


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
