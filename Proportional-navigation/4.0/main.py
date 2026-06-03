# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: main.py
生成时间: 2026-06-03 00:00:00
文件名: main.py
功能说明: 比例导航实验 4.0 主程序 / Main program for proportional-navigation experiment 4.0.
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    DT,
    FIGURE_DIR,
    HIT_RADIUS_M,
    MAX_OVERLOAD_G,
    METRIC_PNG,
    MISSILE_POSITION_M,
    MISSILE_SPEED_MPS,
    NAVIGATION_RATIO,
    SAVE_DIR,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TABLE_DIR,
    TARGET_HEADING_DEG,
    TARGET_NORMAL_G_VALUES,
    TARGET_POSITION_M,
    TARGET_SPEED_MPS,
    TITLE,
    TRAJECTORY_PNG,
    T_MAX_S,
    ensure_directories,
)

G0 = 9.80665


def configure_matplotlib() -> None:
    """
    功能：配置中文字体与负号显示。
    参数：无。
    返回：无。
    调用位置：main() 开始阶段。
    """

    available_fonts = {item.name for item in font_manager.fontManager.ttflist}
    for font_name in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "WenQuanYi Micro Hei", "Arial Unicode MS"):
        if font_name in available_fonts:
            plt.rcParams["font.sans-serif"] = [font_name, *plt.rcParams.get("font.sans-serif", [])]
            break
    plt.rcParams["axes.unicode_minus"] = False


def write_summary(rows: list[dict]) -> None:
    """
    功能：保存目标机动实验结果表格与 JSON 摘要。
    参数：rows 为结果字典列表。
    返回：无。
    调用位置：main() 计算结束后。
    """

    with open(SUMMARY_CSV, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(SUMMARY_JSON, "w", encoding="utf-8") as handle:
        json.dump({"title": TITLE, "results": rows}, handle, ensure_ascii=False, indent=2)


def plot_trajectory(results: list[dict], target_tracks: list[dict]) -> None:
    """
    功能：绘制不同目标机动过载下的拦截轨迹图。
    参数：results 为导弹结果列表，target_tracks 为目标轨迹列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    for item, target in zip(results, target_tracks):
        ax.plot(item["missile_x"], item["missile_y"], label=f"Nt={item['target_normal_g']} g")
        ax.plot(target["target_x"], target["target_y"], linestyle="--", alpha=0.35)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(TITLE)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(TRAJECTORY_PNG, dpi=200)
    plt.close(fig)


def plot_metrics(results: list[dict]) -> None:
    """
    功能：绘制目标机动水平与性能指标关系图。
    参数：results 为实验结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    x_values = [item["target_normal_g"] for item in results]
    need_g = [item["max_required_overload_g"] for item in results]
    miss = [item["miss_distance_m"] for item in results]

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    axes[0].plot(x_values, need_g, marker="o")
    axes[0].set_ylabel("最大需用过载 / g")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[1].plot(x_values, miss, marker="s", color="#b54d1a")
    axes[1].set_xlabel("目标法向机动过载 / g")
    axes[1].set_ylabel("脱靶量 / m")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(METRIC_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行比例导航实验 4.0 的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    results = []
    target_tracks = []

    for target_normal_g in TARGET_NORMAL_G_VALUES:
        x_m, y_m = MISSILE_POSITION_M
        x_t, y_t = TARGET_POSITION_M
        gamma = math.atan2(y_t - y_m, x_t - x_m)
        target_heading = math.radians(TARGET_HEADING_DEG)
        min_range = math.hypot(x_t - x_m, y_t - y_m)
        max_required_g = 0.0
        max_actual_g = 0.0
        saturation_steps = 0
        flight_time_s = 0.0
        intercepted = False

        missile_x = [x_m]
        missile_y = [y_m]
        target_x = [x_t]
        target_y = [y_t]

        for step in range(int(T_MAX_S / DT)):
            vx_m = MISSILE_SPEED_MPS * math.cos(gamma)
            vy_m = MISSILE_SPEED_MPS * math.sin(gamma)
            vx_t = TARGET_SPEED_MPS * math.cos(target_heading)
            vy_t = TARGET_SPEED_MPS * math.sin(target_heading)

            rel_x = x_t - x_m
            rel_y = y_t - y_m
            rel_range = math.hypot(rel_x, rel_y)
            min_range = min(min_range, rel_range)
            if rel_range <= HIT_RADIUS_M:
                intercepted = True
                flight_time_s = step * DT
                break

            rel_vx = vx_t - vx_m
            rel_vy = vy_t - vy_m
            los_rate = (rel_x * rel_vy - rel_y * rel_vx) / max(rel_range**2, 1.0)
            closing_speed = -(rel_x * rel_vx + rel_y * rel_vy) / max(rel_range, 1.0)
            required_g = NAVIGATION_RATIO * max(closing_speed, 0.0) * los_rate / G0
            actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))
            if abs(required_g) > MAX_OVERLOAD_G:
                saturation_steps += 1

            gamma += actual_g * G0 / MISSILE_SPEED_MPS * DT
            if target_normal_g != 0.0:
                target_heading += target_normal_g * G0 / TARGET_SPEED_MPS * DT
            x_m += MISSILE_SPEED_MPS * math.cos(gamma) * DT
            y_m += MISSILE_SPEED_MPS * math.sin(gamma) * DT
            x_t += TARGET_SPEED_MPS * math.cos(target_heading) * DT
            y_t += TARGET_SPEED_MPS * math.sin(target_heading) * DT

            max_required_g = max(max_required_g, abs(required_g))
            max_actual_g = max(max_actual_g, abs(actual_g))
            missile_x.append(x_m)
            missile_y.append(y_m)
            target_x.append(x_t)
            target_y.append(y_t)
            flight_time_s = step * DT

            if step > 20 and closing_speed < 0.0 and rel_range > min_range + 1.0:
                break

        results.append(
            {
                "target_normal_g": target_normal_g,
                "max_required_overload_g": round(max_required_g, 6),
                "max_actual_overload_g": round(max_actual_g, 6),
                "miss_distance_m": round(min_range, 6),
                "intercepted": intercepted,
                "flight_time_s": round(flight_time_s, 6),
                "saturation_ratio": round(saturation_steps / max(1, len(missile_x) - 1), 6),
                "missile_x": missile_x,
                "missile_y": missile_y,
            }
        )
        target_tracks.append({"target_x": target_x, "target_y": target_y})

    write_summary([{k: v for k, v in item.items() if k not in ("missile_x", "missile_y")} for item in results])
    # 绘制不同目标机动水平下的轨迹图。
    plot_trajectory(results, target_tracks)
    # 绘制目标机动影响统计图。
    plot_metrics(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
