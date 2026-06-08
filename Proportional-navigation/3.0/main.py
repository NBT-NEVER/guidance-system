# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
生成时间: 2026-06-03 00:00:00
文件名: main.py
功能说明: 比例导航实验 3.0 主程序 / Main program for proportional-navigation experiment 3.0.
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    CONVERGENCE_THRESHOLD_M,
    DT,
    FIGURE_DIR,
    HIT_RADIUS_M,
    MAX_OVERLOAD_G,
    METRIC_PNG,
    MISSILE_POSITION_M,
    NAVIGATION_RATIO_SCAN,
    SAVE_DIR,
    SPEED_RATIO_VALUES,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TABLE_DIR,
    TARGET_HEADING_DEG,
    TARGET_POSITION_M,
    TARGET_SPEED_MPS,
    TITLE,
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
    功能：保存最小导航比搜索结果表格与 JSON 摘要。
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


def plot_metrics(results: list[dict]) -> None:
    """
    功能：绘制速度比与最小导航比关系图。
    参数：results 为实验结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(
        [item["speed_ratio"] for item in results],
        [math.nan if item["min_navigation_ratio"] is None else item["min_navigation_ratio"] for item in results],
        marker="o",
    )
    ax.set_xlabel("弹目速度比 P")
    ax.set_ylabel("最小导航比 Kmin")
    ax.set_title(TITLE)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(METRIC_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行比例导航实验 3.0 的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    results = []

    for speed_ratio in SPEED_RATIO_VALUES:
        missile_speed_mps = speed_ratio * TARGET_SPEED_MPS
        found_value = None

        for navigation_ratio in NAVIGATION_RATIO_SCAN:
            x_m, y_m = MISSILE_POSITION_M
            x_t, y_t = TARGET_POSITION_M
            gamma = math.atan2(y_t - y_m, x_t - x_m)
            target_heading = math.radians(TARGET_HEADING_DEG)
            min_range = math.hypot(x_t - x_m, y_t - y_m)
            intercepted = False

            for step in range(int(T_MAX_S / DT)):
                vx_m = missile_speed_mps * math.cos(gamma)
                vy_m = missile_speed_mps * math.sin(gamma)
                vx_t = TARGET_SPEED_MPS * math.cos(target_heading)
                vy_t = TARGET_SPEED_MPS * math.sin(target_heading)

                rel_x = x_t - x_m
                rel_y = y_t - y_m
                rel_range = math.hypot(rel_x, rel_y)
                min_range = min(min_range, rel_range)
                if rel_range <= HIT_RADIUS_M:
                    intercepted = True
                    break

                rel_vx = vx_t - vx_m
                rel_vy = vy_t - vy_m
                los_rate = (rel_x * rel_vy - rel_y * rel_vx) / max(rel_range**2, 1.0)
                closing_speed = -(rel_x * rel_vx + rel_y * rel_vy) / max(rel_range, 1.0)
                required_g = navigation_ratio * max(closing_speed, 0.0) * los_rate / G0
                actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))

                gamma += actual_g * G0 / missile_speed_mps * DT
                x_m += missile_speed_mps * math.cos(gamma) * DT
                y_m += missile_speed_mps * math.sin(gamma) * DT
                x_t += TARGET_SPEED_MPS * math.cos(target_heading) * DT
                y_t += TARGET_SPEED_MPS * math.sin(target_heading) * DT

                if step > 20 and closing_speed < 0.0 and rel_range > min_range + 1.0:
                    break

            if intercepted and min_range < CONVERGENCE_THRESHOLD_M:
                found_value = round(float(navigation_ratio), 1)
                break

        results.append(
            {
                "speed_ratio": speed_ratio,
                "missile_speed_mps": round(missile_speed_mps, 3),
                "target_speed_mps": round(TARGET_SPEED_MPS, 3),
                "min_navigation_ratio": found_value,
                "reachable": found_value is not None,
            }
        )

    write_summary(results)
    # 绘制速度比与最小导航比的关系图。
    plot_metrics(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
