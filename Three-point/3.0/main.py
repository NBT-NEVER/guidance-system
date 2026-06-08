# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
生成时间: 2026-06-03 00:00:00
文件名: main.py
功能说明: 三点法实验 3.0 主程序 / Main program for three-point experiment 3.0.
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    BASELINE_KC,
    BASELINE_KD,
    BASELINE_KE,
    DT,
    FIGURE_DIR,
    HIT_RADIUS_M,
    LAW_CASES,
    MAX_OVERLOAD_G,
    METRIC_PNG,
    MISSILE_POSITION_M,
    MISSILE_VELOCITY_MPS,
    SAVE_DIR,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TABLE_DIR,
    TARGET_NORMAL_G_VALUES,
    TARGET_POSITION_M,
    TARGET_VELOCITY_MPS,
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
    功能：保存目标机动对比结果表格与 JSON 摘要。
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
    功能：绘制目标机动条件下三种方法的指标对比图。
    参数：results 为实验结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    for law_name in {item["law_name"] for item in results}:
        subset = sorted([item for item in results if item["law_name"] == law_name], key=lambda row: row["target_normal_g"])
        x_values = [item["target_normal_g"] for item in subset]
        axes[0].plot(x_values, [item["max_required_overload_g"] for item in subset], marker="o", label=law_name)
        axes[1].plot(x_values, [item["terminal_overload_g"] for item in subset], marker="s", label=law_name)
        axes[2].plot(x_values, [item["miss_distance_m"] for item in subset], marker="^", label=law_name)
    axes[0].set_ylabel("最大需用过载 / g")
    axes[1].set_ylabel("末端过载 / g")
    axes[2].set_ylabel("脱靶量 / m")
    axes[2].set_xlabel("目标机动过载 / g")
    for axis in axes:
        axis.grid(True, linestyle="--", alpha=0.4)
        axis.legend()
    fig.tight_layout()
    fig.savefig(METRIC_PNG, dpi=200)
    plt.close(fig)


def plot_trajectory(results: list[dict], target_tracks: list[dict]) -> None:
    """
    功能：绘制代表性目标机动工况下的轨迹对比图。
    参数：results 为导弹结果列表，target_tracks 为目标轨迹列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    representative = TARGET_NORMAL_G_VALUES[1]
    selected = [item for item in results if item["target_normal_g"] == representative]
    selected_targets = target_tracks[: len(selected)]

    fig, ax = plt.subplots(figsize=(9, 6))
    for item, target in zip(selected, selected_targets):
        ax.plot(item["missile_x"], item["missile_y"], label=item["law_name"])
        ax.plot(target["target_x"], target["target_y"], linestyle="--", alpha=0.4)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(f"{TITLE}（Nt={representative} g）")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(TRAJECTORY_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行三点法实验 3.0 的全部计算、统计与绘图。
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
        for law_case in LAW_CASES:
            x_m, y_m = MISSILE_POSITION_M
            x_t, y_t = TARGET_POSITION_M
            missile_speed_mps = math.hypot(*MISSILE_VELOCITY_MPS)
            target_speed_mps = math.hypot(*TARGET_VELOCITY_MPS)
            gamma = math.atan2(MISSILE_VELOCITY_MPS[1], MISSILE_VELOCITY_MPS[0])
            target_heading = math.atan2(TARGET_VELOCITY_MPS[1], TARGET_VELOCITY_MPS[0])
            prev_line_error = 0.0
            prev_ref_angle = math.atan2(y_t, x_t)
            min_range = math.hypot(x_t - x_m, y_t - y_m)
            max_required_g = 0.0
            max_actual_g = 0.0
            terminal_g = 0.0
            flight_time_s = 0.0
            intercepted = False

            missile_x = [x_m]
            missile_y = [y_m]
            target_x = [x_t]
            target_y = [y_t]

            for step in range(int(T_MAX_S / DT)):
                vx_m = missile_speed_mps * math.cos(gamma)
                vy_m = missile_speed_mps * math.sin(gamma)
                vx_t = target_speed_mps * math.cos(target_heading)
                vy_t = target_speed_mps * math.sin(target_heading)

                range_mt = math.hypot(x_t - x_m, y_t - y_m)
                min_range = min(min_range, range_mt)
                if range_mt <= HIT_RADIUS_M:
                    intercepted = True
                    flight_time_s = step * DT
                    break

                station_range_t = max(math.hypot(x_t, y_t), 1.0)
                theta_t = math.atan2(y_t, x_t)
                target_los_rate = (x_t * vy_t - y_t * vx_t) / max(x_t**2 + y_t**2, 1.0)
                rel_vx = vx_t - vx_m
                rel_vy = vy_t - vy_m
                closing_speed = -((x_t - x_m) * rel_vx + (y_t - y_m) * rel_vy) / max(range_mt, 1.0)
                t_go = range_mt / max(closing_speed, 1.0)
                theta_ref = theta_t + law_case["lead_factor"] * target_los_rate * t_go
                theta_ref_dot = (theta_ref - prev_ref_angle) / DT
                line_error = x_m * math.sin(theta_ref) - y_m * math.cos(theta_ref)
                line_error_rate = (line_error - prev_line_error) / DT
                gamma_dot_cmd = -(
                    BASELINE_KE * line_error / station_range_t
                    + BASELINE_KD * line_error_rate / max(missile_speed_mps, 1.0)
                    + BASELINE_KC * theta_ref_dot
                )
                required_g = missile_speed_mps * gamma_dot_cmd / G0
                actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))

                gamma += actual_g * G0 / missile_speed_mps * DT
                if target_normal_g != 0.0:
                    target_heading += target_normal_g * G0 / target_speed_mps * DT
                x_m += missile_speed_mps * math.cos(gamma) * DT
                y_m += missile_speed_mps * math.sin(gamma) * DT
                x_t += target_speed_mps * math.cos(target_heading) * DT
                y_t += target_speed_mps * math.sin(target_heading) * DT

                prev_line_error = line_error
                prev_ref_angle = theta_ref
                max_required_g = max(max_required_g, abs(required_g))
                max_actual_g = max(max_actual_g, abs(actual_g))
                terminal_g = actual_g
                missile_x.append(x_m)
                missile_y.append(y_m)
                target_x.append(x_t)
                target_y.append(y_t)
                flight_time_s = step * DT

                if step > 20 and closing_speed < 0.0 and range_mt > min_range + 1.0:
                    break

            results.append(
                {
                    "law_name": law_case["law_name"],
                    "target_normal_g": target_normal_g,
                    "max_required_overload_g": round(max_required_g, 6),
                    "max_actual_overload_g": round(max_actual_g, 6),
                    "terminal_overload_g": round(abs(terminal_g), 6),
                    "miss_distance_m": round(min_range, 6),
                    "intercepted": intercepted,
                    "flight_time_s": round(flight_time_s, 6),
                    "missile_x": missile_x,
                    "missile_y": missile_y,
                }
            )
            target_tracks.append({"target_x": target_x, "target_y": target_y})

    write_summary([{k: v for k, v in item.items() if k not in ("missile_x", "missile_y")} for item in results])
    # 绘制目标机动影响下的指标对比图。
    plot_metrics(results)
    # 绘制代表性目标机动工况下的轨迹图。
    plot_trajectory(results, target_tracks)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
