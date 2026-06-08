# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-03 00:00:00
文件名: config.py
功能说明:追踪法允许攻击区分析配置文件
版本号：4.0
"""

from pathlib import Path

# 实验根目录
PROJECT_ROOT = Path(__file__).resolve().parent
print(f"当前实验根目录: {PROJECT_ROOT}")
# 输出根目录
SAVE_DIR = PROJECT_ROOT / "outputs"
# 表格输出目录
TABLE_DIR = SAVE_DIR / "tables"
# 图像输出目录
FIGURE_DIR = SAVE_DIR / "figures"
SUMMARY_CSV = TABLE_DIR / "summary.csv"
SUMMARY_JSON = TABLE_DIR / "summary.json"
ATTACK_PNG = FIGURE_DIR / "attack_zone.png"
CARTESIAN_MISS_PNG = FIGURE_DIR / "attack_zone_cartesian_miss.png"

TITLE = "实验 4.0：追踪法允许攻击区判定"

DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 5.0
#攻击半径
MAX_OVERLOAD_G = 20.0

MISSILE_SPEED_MPS = 1.2 * 340
TARGET_SPEED_MPS = 0.8 * 340
TARGET_HEADING_DEG = 0.0
RANGE_VALUES_M = [
    500.0, 750.0, 1000.0, 1250.0, 1500.0, 1750.0, 2000.0, 2250.0, 2500.0, 2750.0,
    3000.0, 3250.0, 3500.0, 3750.0, 4000.0, 4250.0, 4500.0, 4750.0, 5000.0,
]
LOS_VALUES_DEG = list(range(0, 181, 5))


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
