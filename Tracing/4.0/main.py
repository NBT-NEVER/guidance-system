# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: main.py
生成时间: 2026-06-03 00:00:00
文件名: main.py
功能说明: 追踪法实验 4.0 主程序 / Main program for tracing experiment 4.0.
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    ATTACK_PNG,
    DT,
    FIGURE_DIR,
    HIT_RADIUS_M,
    LOS_VALUES_DEG,
    MAX_OVERLOAD_G,
    MISSILE_SPEED_MPS,
    RANGE_VALUES_M,
    SAVE_DIR,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TABLE_DIR,
    TARGET_HEADING_DEG,
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
    功能：保存攻击区判定结果表格与 JSON 摘要。
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


def plot_attack_zone(results: list[dict]) -> None:
    """
    功能：绘制追踪法允许攻击区散点图。
    参数：results 为网格扫描结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    for item in results:
        color = "#2d8c4d" if item["feasible"] else "#c24b37"
        ax.scatter(item["initial_los_deg"], item["initial_range_m"], c=color, s=20)
    ax.set_xlabel("初始视线角 / deg")
    ax.set_ylabel("初始弹目距离 / m")
    ax.set_title(TITLE)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(ATTACK_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行追踪法实验 4.0 的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    results = []

    for initial_range_m in RANGE_VALUES_M:
        for initial_los_deg in LOS_VALUES_DEG:
            x_m = 0.0
            y_m = 0.0
            los0 = math.radians(initial_los_deg)
            x_t = initial_range_m * math.cos(los0)
            y_t = initial_range_m * math.sin(los0)
            gamma = los0
            target_heading = math.radians(TARGET_HEADING_DEG)
            min_range = initial_range_m
            max_required_g = 0.0
            max_actual_g = 0.0
            saturation_steps = 0
            flight_time_s = 0.0
            intercepted = False

            for step in range(int(T_MAX_S / DT)):
                rel_x = x_t - x_m
                rel_y = y_t - y_m
                rel_range = math.hypot(rel_x, rel_y)
                min_range = min(min_range, rel_range)
                if rel_range <= HIT_RADIUS_M:
                    intercepted = True
                    flight_time_s = step * DT
                    break

                desired_heading = math.atan2(rel_y, rel_x)
                heading_error = desired_heading - gamma
                while heading_error > math.pi:
                    heading_error -= 2.0 * math.pi
                while heading_error < -math.pi:
                    heading_error += 2.0 * math.pi

                gamma_dot_cmd = heading_error / DT
                required_g = MISSILE_SPEED_MPS * gamma_dot_cmd / G0
                actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))
                if abs(required_g) > MAX_OVERLOAD_G:
                    saturation_steps += 1

                gamma += actual_g * G0 / MISSILE_SPEED_MPS * DT
                x_m += MISSILE_SPEED_MPS * math.cos(gamma) * DT
                y_m += MISSILE_SPEED_MPS * math.sin(gamma) * DT
                x_t += TARGET_SPEED_MPS * math.cos(target_heading) * DT
                y_t += TARGET_SPEED_MPS * math.sin(target_heading) * DT

                max_required_g = max(max_required_g, abs(required_g))
                max_actual_g = max(max_actual_g, abs(actual_g))
                flight_time_s = step * DT

                closing_speed = (
                    rel_x * (TARGET_SPEED_MPS * math.cos(target_heading) - MISSILE_SPEED_MPS * math.cos(gamma))
                    + rel_y * (TARGET_SPEED_MPS * math.sin(target_heading) - MISSILE_SPEED_MPS * math.sin(gamma))
                ) / max(rel_range, 1.0)
                if step > 10 and closing_speed > 0.0 and rel_range > min_range + 1.0:
                    break

            feasible = intercepted and max_required_g <= MAX_OVERLOAD_G
            results.append(
                {
                    "initial_range_m": initial_range_m,
                    "initial_los_deg": initial_los_deg,
                    "max_required_overload_g": round(max_required_g, 6),
                    "max_actual_overload_g": round(max_actual_g, 6),
                    "miss_distance_m": round(min_range, 6),
                    "intercepted": intercepted,
                    "flight_time_s": round(flight_time_s, 6),
                    "saturation_ratio": round(saturation_steps / max(1, int(flight_time_s / DT) + 1), 6),
                    "feasible": feasible,
                }
            )

    write_summary(results)
    # 绘制当前实验的允许攻击区判定图。
    plot_attack_zone(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
