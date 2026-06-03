# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: config.py
生成时间: 2026-06-03 00:00:00
文件名: config.py
功能说明: 追踪法实验一独立配置 / Independent configuration for tracing experiment 1.0.
"""

from pathlib import Path

# 当前实验目录
PROJECT_ROOT = Path(__file__).resolve().parent
# 结果根目录
SAVE_DIR = PROJECT_ROOT / "outputs"
# 表格输出目录
TABLE_DIR = SAVE_DIR / "tables"
# 图像输出目录
FIGURE_DIR = SAVE_DIR / "figures"

SUMMARY_CSV = TABLE_DIR / "summary.csv"
SUMMARY_JSON = TABLE_DIR / "summary.json"
TRAJECTORY_PNG = FIGURE_DIR / "trajectory.png"
METRIC_PNG = FIGURE_DIR / "metrics.png"

TITLE = "实验一（中等）：追踪法导引方法—速度比 P 对导引弹道的影响"
DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 5.0
MAX_OVERLOAD_G = 20.0
INITIAL_RANGE_M = 4000.0
INITIAL_LOS_DEG = 90.0
TARGET_HEADING_DEG = 0.0
TARGET_SPEED_MPS = 0.8 * 340.0
SPEED_RATIO_VALUES = [0.5, 0.8, 1.0, 1.4, 1.5, 1.8, 2.0, 2.2, 2.5]


def ensure_directories() -> None:
    """
    功能：创建当前实验需要的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
