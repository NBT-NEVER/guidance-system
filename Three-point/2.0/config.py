# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: config.py
开发时间: 2026-06-03 00:00:00
文件名: config.py
功能说明:三点法三点法前置量法半前置量法对比分析配置文件
版本号：2.0
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

TITLE = "实验 2.0：三点法、前置量法与半前置量法对比"

DT = 0.01
T_MAX_S = 80.0
HIT_RADIUS_M = 10.0
MAX_OVERLOAD_G = 20.0

BASELINE_KE = 1.2
BASELINE_KD = 0.8
BASELINE_KC = 0.6

LAW_CASES = [
    {"law_name": "三点法", "lead_factor": 0.0},
    {"law_name": "前置量法", "lead_factor": 1.0},
    {"law_name": "半前置量法", "lead_factor": 0.5},
]

ELEVATION_CASES = [
    {
        "elevation_deg": 30,
        "missile_position_m": (2600.0, 1500.0),
        "target_position_m": (6500.0, 3750.0),
        "missile_velocity_mps": (390.0, 225.0),
        "target_velocity_mps": (240.0, 0.0),
    },
    {
        "elevation_deg": 45,
        "missile_position_m": (2100.0, 2100.0),
        "target_position_m": (5300.0, 5300.0),
        "missile_velocity_mps": (320.0, 320.0),
        "target_velocity_mps": (240.0, 0.0),
    },
    {
        "elevation_deg": 60,
        "missile_position_m": (1500.0, 2600.0),
        "target_position_m": (3750.0, 6500.0),
        "missile_velocity_mps": (225.0, 390.0),
        "target_velocity_mps": (240.0, 0.0),
    },
    {
        "elevation_deg": 75,
        "missile_position_m": (775.0, 2900.0),
        "target_position_m": (1940.0, 7240.0),
        "missile_velocity_mps": (115.0, 435.0),
        "target_velocity_mps": (240.0, 0.0),
    },
]


def ensure_directories() -> None:
    """
    功能：创建当前实验运行所需的输出目录。
    参数：无。
    返回：无。
    调用位置：main.py 入口初始化阶段。
    """

    for folder in (SAVE_DIR, TABLE_DIR, FIGURE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
