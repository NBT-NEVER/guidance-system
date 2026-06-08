# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
生成时间: 2026-06-03 00:00:00
文件名: config.py
功能说明: 比例导引实验一独立配置 / Independent configuration for proportional-navigation experiment 1.0.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SAVE_DIR = PROJECT_ROOT / "outputs"
TABLE_DIR = SAVE_DIR / "tables"
FIGURE_DIR = SAVE_DIR / "figures"

SUMMARY_CSV = TABLE_DIR / "summary.csv"
SUMMARY_JSON = TABLE_DIR / "summary.json"
TRAJECTORY_PNG = FIGURE_DIR / "trajectory.png"
METRIC_PNG = FIGURE_DIR / "metrics.png"

TITLE = "实验一（容易）：比例导引法—导航比对导引弹道的影响"
DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 0.1
MAX_OVERLOAD_G = 20.0
MISSILE_POSITION_M = (0.0, 0.0)
TARGET_POSITION_M = (10000.0, 3000.0)
MISSILE_SPEED_MPS = 500.0
TARGET_SPEED_MPS = 300.0
TARGET_HEADING_DEG = 180.0
NAVIGATION_RATIO_VALUES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]


def ensure_directories() -> None:
    """
    功能：创建当前实验需要的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
