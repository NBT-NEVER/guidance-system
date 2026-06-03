# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: config.py
生成时间: 2026-06-03 15:59:50
文件名: config.py
功能说明: 比例导引实验五 配置文件 / Configuration for proportional-navigation experiment.
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

EXPERIMENT = {'title': '实验五（困难）：比例导引法—计算允许攻击区',
'mode': 'attack_zone',
'dt': 0.01,
't_max_s': 80.0,
'hit_radius_m': 0.1,
'max_overload_g': 10.0,
'navigation_ratio': 4.0,
'base_scenario': {'target_position_m': [0.0, 0.0],
           'missile_speed_mps': 500.0,
           'target_speed_mps': 400.0,
           'target_heading_deg': 0.0},
'launch_scan': {'radius_values_m': [125,
                             250,
                             375,
                             500,
                             625,
                             750,
                             875,
                             1000,
                             1125,
                             1250,
                             1375,
                             1500,
                             1625,
                             1750,
                             1875,
                             2000,
                             2125,
                             2250,
                             2375,
                             2500],
         'angle_values_deg': [0,
                              5,
                              10,
                              15,
                              20,
                              25,
                              30,
                              35,
                              40,
                              45,
                              50,
                              55,
                              60,
                              65,
                              70,
                              75,
                              80,
                              85,
                              90,
                              95,
                              100,
                              105,
                              110,
                              115,
                              120,
                              125,
                              130,
                              135,
                              140,
                              145,
                              150,
                              155,
                              160,
                              165,
                              170,
                              175,
                              180,
                              185,
                              190,
                              195,
                              200,
                              205,
                              210,
                              215,
                              220,
                              225,
                              230,
                              235,
                              240,
                              245,
                              250,
                              255,
                              260,
                              265,
                              270,
                              275,
                              280,
                              285,
                              290,
                              295,
                              300,
                              305,
                              310,
                              315,
                              320,
                              325,
                              330,
                              335,
                              340,
                              345,
                              350,
                              355]}}


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
