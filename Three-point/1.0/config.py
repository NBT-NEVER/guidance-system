# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-03 00:00:00
文件名: config.py
功能说明:三点法制导律参数影响分析配置文件
版本号：1.0
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SAVE_DIR = PROJECT_ROOT / "outputs"
TABLE_DIR = SAVE_DIR / "tables"
FIGURE_DIR = SAVE_DIR / "figures"

SUMMARY_CSV = TABLE_DIR / "summary.csv"
SUMMARY_JSON = TABLE_DIR / "summary.json"
METRIC_PNG = FIGURE_DIR / "metrics.png"

TITLE = "实验一（中等）：三点法制导律参数对导引弹道特性的影响"
DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 10.0
MAX_OVERLOAD_G = 3.0
MISSILE_POSITION_M = (1000.0, 3000.0)
TARGET_POSITION_M = (2500.0, 7500.0)
MISSILE_VELOCITY_MPS = (140.0, 420.0)
TARGET_VELOCITY_MPS = (240.0, 0.0)
BASELINE_KE = 1.2
BASELINE_KD = 0.8
BASELINE_KC = 0.6
KE_VALUES = [round(0.1 * idx, 1) for idx in range(1, 31)]
KD_VALUES = [round(0.1 * idx, 1) for idx in range(0, 21)]
KC_VALUES = [round(0.1 * idx, 1) for idx in range(0, 21)]


def ensure_directories() -> None:
    """
    功能：创建当前实验需要的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
