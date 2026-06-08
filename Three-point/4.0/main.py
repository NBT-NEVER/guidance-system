# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
生成时间: 2026-06-03 00:00:00
文件名: main.py
功能说明: 三点法实验 4.0 主程序 / Main program for three-point experiment 4.0.
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
    BASELINE_KC,
    BASELINE_KD,
    BASELINE_KE,
    DT,
    ELEVATION_VALUES_DEG,
    FIGURE_DIR,
    HIT_RADIUS_M,
    LIMIT_OVERLOAD_VALUES_G,
    MAX_OVERLOAD_G,
    MISSILE_SPEED_MPS,
    SAVE_DIR,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TABLE_DIR,
    TARGET_ALTITUDE_M,
    TARGET_VELOCITY_MPS,
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
    功能：保存攻击禁区判定结果表格与 JSON 摘要。
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
    功能：绘制三点法攻击禁区判定散点图。
    参数：results 为不同角度和过载约束下的结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    for item in results:
        color = "#2d8c4d" if item["feasible"] else "#c24b37"
        ax.scatter(item["elevation_deg"], item["limit_overload_g"], c=color, s=22)
    ax.set_xlabel("发射高低角 / deg")
    ax.set_ylabel("允许过载上限 / g")
    ax.set_title(TITLE)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(ATTACK_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行三点法实验 4.0 的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    results = []

    for limit_overload_g in LIMIT_OVERLOAD_VALUES_G:
        for elevation_deg in ELEVATION_VALUES_DEG:
            theta = math.radians(elevation_deg)
            x_m, y_m = 0.0, 0.0
            x_t, y_t = TARGET_ALTITUDE_M / max(math.tan(theta), 1e-6), TARGET_ALTITUDE_M
            missile_velocity_mps = (
                MISSILE_SPEED_MPS * math.cos(theta),
                MISSILE_SPEED_MPS * math.sin(theta),
            )
            missile_speed_mps = MISSILE_SPEED_MPS
            target_speed_mps = math.hypot(*TARGET_VELOCITY_MPS)
            gamma = theta
            target_heading = math.atan2(TARGET_VELOCITY_MPS[1], TARGET_VELOCITY_MPS[0])
            prev_line_error = 0.0
            prev_ref_angle = math.atan2(y_t, x_t)
            min_range = math.hypot(x_t - x_m, y_t - y_m)
            max_required_g = 0.0
            flight_time_s = 0.0
            intercepted = False

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
                theta_ref = theta_t
                theta_ref_dot = (theta_ref - prev_ref_angle) / DT
                line_error = x_m * math.sin(theta_ref) - y_m * math.cos(theta_ref)
                line_error_rate = (line_error - prev_line_error) / DT
                gamma_dot_cmd = -(
                    BASELINE_KE * line_error / station_range_t
                    + BASELINE_KD * line_error_rate / max(missile_speed_mps, 1.0)
                    + BASELINE_KC * theta_ref_dot
                )
                required_g = missile_speed_mps * gamma_dot_cmd / G0
                actual_g = max(-limit_overload_g, min(limit_overload_g, required_g))

                gamma += actual_g * G0 / missile_speed_mps * DT
                x_m += missile_speed_mps * math.cos(gamma) * DT
                y_m += missile_speed_mps * math.sin(gamma) * DT
                x_t += target_speed_mps * math.cos(target_heading) * DT
                y_t += target_speed_mps * math.sin(target_heading) * DT

                prev_line_error = line_error
                prev_ref_angle = theta_ref
                max_required_g = max(max_required_g, abs(required_g))
                flight_time_s = step * DT

                rel_vx = vx_t - vx_m
                rel_vy = vy_t - vy_m
                closing_speed = -((x_t - x_m) * rel_vx + (y_t - y_m) * rel_vy) / max(range_mt, 1.0)
                if step > 20 and closing_speed < 0.0 and range_mt > min_range + 1.0:
                    break

            feasible = intercepted and max_required_g <= limit_overload_g
            results.append(
                {
                    "elevation_deg": elevation_deg,
                    "limit_overload_g": limit_overload_g,
                    "target_initial_x_m": round(TARGET_ALTITUDE_M / max(math.tan(theta), 1e-6), 6),
                    "target_initial_y_m": TARGET_ALTITUDE_M,
                    "max_required_overload_g": round(max_required_g, 6),
                    "miss_distance_m": round(min_range, 6),
                    "intercepted": intercepted,
                    "flight_time_s": round(flight_time_s, 6),
                    "feasible": feasible,
                }
            )

    write_summary(results)
    # 绘制当前实验的攻击禁区判定图。
    plot_attack_zone(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
