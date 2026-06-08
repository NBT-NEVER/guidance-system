# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-03 00:00:00
文件名: config.py
功能说明:三点法攻击禁区分析配置文件
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

TITLE = "实验 4.0：三点法攻击禁区判定"

DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 10.0
MAX_OVERLOAD_G = 10.0

BASELINE_KE = 1.2
BASELINE_KD = 0.8
BASELINE_KC = 0.6
TARGET_ALTITUDE_M = 7000.0
TARGET_VELOCITY_MPS = (240.0, 0.0)
MISSILE_SPEED_MPS = 450.0
ELEVATION_VALUES_DEG = list(range(10, 91, 2))
LIMIT_OVERLOAD_VALUES_G = [1.0, 3.0, 5.0, 10.0]


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
