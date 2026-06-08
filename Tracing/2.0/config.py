# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
生成时间: 2026-06-03 00:00:00
文件名: config.py
功能说明: 追踪法实验 2.0 配置文件 / Configuration for tracing experiment 2.0.
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
TRAJECTORY_PNG = FIGURE_DIR / "trajectory.png"
METRIC_PNG = FIGURE_DIR / "metrics.png"

TITLE = "实验 2.0：追踪法中初始视线角对拦截过程的影响"

DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 5.0
MAX_OVERLOAD_G = 20.0

MISSILE_SPEED_MPS = 408.0
TARGET_SPEED_MPS = 272.0
INITIAL_RANGE_M = 4000.0
TARGET_HEADING_DEG = 0.0
INITIAL_LOS_VALUES_DEG = [20.0, 40.0, 60.0, 90.0, 120.0, 140.0, 160.0]


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
