# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
生成时间: 2026-06-03 00:00:00
文件名: config.py
功能说明: 比例导航实验 6.0 配置文件 / Configuration for proportional-navigation experiment 6.0.
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

TITLE = "实验 6.0：带姿态回路的比例导航拦截对比"

DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 0.1
MAX_OVERLOAD_G = 20.0
NAVIGATION_RATIO = 5.0

MISSILE_POSITION_M = (0.0, 0.0)
TARGET_POSITION_M = (10000.0, 3000.0)
MISSILE_SPEED_MPS = 500.0
TARGET_SPEED_MPS = 300.0
TARGET_HEADING_DEG = 180.0
ZETA = 0.707
OMEGA_N = 10.0


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
