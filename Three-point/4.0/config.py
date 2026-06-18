# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-18 00:00:00
文件名: config.py
功能说明: 三点法攻击禁区图实验配置
版本号：4.0
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
ATTACK_PNG = FIGURE_DIR / "attack_zone.png"
ATTACK_SPATIAL_COMBINED_PNG = FIGURE_DIR / "attack_zone_spatial_combined.png"

TITLE = "实验 4.0：三点法攻击禁区图"

TARGET_ALTITUDE_M = 7000.0
MISSILE_SPEED_MPS = 450.0
TARGET_SPEED_MPS = 240.0
MISSILE_CLIMB_ANGLE_DEG = 90.0

LIMIT_OVERLOAD_VALUES_G = [1.0, 1.5, 2.0, 2.5]
FULL_ATTACK_THRESHOLD_G = 2.5

TARGET_X_MIN_M = -55000.0
TARGET_X_MAX_M = 25000.0
TARGET_X_STEP_M = 5000.0

LEFT_BOUNDARY_BASE_FACTOR = 1.0
LEFT_BOUNDARY_GAIN_FACTOR = 3.3
LEFT_BOUNDARY_EXP = 1.05
RIGHT_BOUNDARY_GAIN_FACTOR = 2.15
RIGHT_BOUNDARY_EXP = 1.18
CURVE_SAMPLE_COUNT = 140


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
