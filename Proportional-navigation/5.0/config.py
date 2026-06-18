# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-09 00:00:00
文件名: config.py
功能说明: 比例导引法允许攻击区计算配置文件
版本号：5.0
"""

from pathlib import Path

# 当前实验根目录。
PROJECT_ROOT = Path(__file__).resolve().parent
print(f"当前实验根目录: {PROJECT_ROOT}")
# 当前实验输出根目录。
SAVE_DIR = PROJECT_ROOT / "outputs"
# 表格输出目录。
TABLE_DIR = SAVE_DIR / "tables"
# 图像输出目录。
FIGURE_DIR = SAVE_DIR / "figures"

SUMMARY_CSV = TABLE_DIR / "summary.csv"
SUMMARY_JSON = TABLE_DIR / "summary.json"
ATTACK_PNG = FIGURE_DIR / "attack_zone.png"
PARAMETER_ATTACK_PNG = FIGURE_DIR / "attack_zone_parameter_plane.png"

TITLE = "实验 5.0：比例导引法允许攻击区计算"

DT = 0.01
T_MAX_S = 60.0
MISS_DISTANCE_THRESHOLD_M = 0.1
MAX_OVERLOAD_G = 15.0
NAVIGATION_RATIO = 4.0

TARGET_POSITION_M = (0.0, 0.0)
TARGET_SPEED_MPS = 400.0
TARGET_HEADING_DEG = 0.0
MISSILE_SPEED_MPS = 500.0

RADIUS_VALUES_M = [float(value) for value in range(125, 2501, 125)]
ANGLE_VALUES_DEG = list(range(0, 360, 5))


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
