# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: config.py
生成时间: 2026-06-03 15:59:50
文件名: config.py
功能说明: 比例导引实验三 配置文件 / Configuration for proportional-navigation experiment.
"""

from pathlib import Path

# 项目路径统一放在配置文件顶部，便于后续实验直接修改。
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SAVE_DIR = PROJECT_ROOT / "outputs"
OUT_DIR = SAVE_DIR / "tables"
FIGURE_DIR = SAVE_DIR / "figures"
MODEL_DIR = PROJECT_ROOT / "models"
LOG_DIR = PROJECT_ROOT / "logs"

SUMMARY_CSV = OUT_DIR / "summary.csv"
DETAIL_JSON = OUT_DIR / "summary.json"
TRAJECTORY_PNG = FIGURE_DIR / "trajectory.png"
METRIC_PNG = FIGURE_DIR / "metrics.png"
ATTACK_PNG = FIGURE_DIR / "attack_zone.png"

EXPERIMENT = {'title': '实验三（中等）：比例导引法—考察速度比值对最小导航比的影响',
'mode': 'minimum_navigation_ratio',
'dt': 0.01,
't_max_s': 100.0,
'hit_radius_m': 0.1,
'max_overload_g': 20.0,
'convergence_threshold_m': 0.1,
'base_scenario': {'missile_position_m': [0.0, 0.0],
           'target_position_m': [10000.0, 2000.0],
           'target_speed_mps': 300.0,
           'target_heading_deg': 180.0},
'speed_ratio_values': [0.6, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0],
'search_range': {'start': 1.0, 'stop': 10.0, 'step': 0.1}}


def build_config() -> dict:
    """
    功能：汇总路径信息与实验参数，生成主程序可直接使用的配置对象。
    参数：无。
    返回：包含路径、输出文件名和实验配置项的字典。
    调用位置：main.py 程序入口与实验分支调度逻辑。
    """

    return {
        "project_root": PROJECT_ROOT,
        "data_dir": DATA_DIR,
        "save_dir": SAVE_DIR,
        "out_dir": OUT_DIR,
        "figure_dir": FIGURE_DIR,
        "model_dir": MODEL_DIR,
        "log_dir": LOG_DIR,
        "summary_csv": SUMMARY_CSV,
        "detail_json": DETAIL_JSON,
        "trajectory_png": TRAJECTORY_PNG,
        "metric_png": METRIC_PNG,
        "attack_png": ATTACK_PNG,
        **EXPERIMENT,
    }


def ensure_directories() -> None:
    """
    功能：创建实验运行所需的目录，避免保存图表和表格时路径不存在。
    参数：无。
    返回：无。
    调用位置：main.py 运行前的初始化阶段与 config.py 自检入口。
    """

    for folder in (DATA_DIR, SAVE_DIR, OUT_DIR, FIGURE_DIR, MODEL_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_directories()
    cfg = build_config()
    print("关键路径清单：")
    for key in ("project_root", "data_dir", "save_dir", "out_dir", "figure_dir", "log_dir"):
        print(f"{key} -> {cfg[key]}")
    print("\n当前目录已有文件：")
    for folder in (PROJECT_ROOT, DATA_DIR, SAVE_DIR, OUT_DIR, FIGURE_DIR, LOG_DIR):
        if folder.exists():
            names = [item.name for item in folder.iterdir()]
            print(f"{folder.name}: {names if names else '空目录'}")
