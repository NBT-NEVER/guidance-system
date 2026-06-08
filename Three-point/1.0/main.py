# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
开发时间: 2026-06-03 00:00:00
文件名: main.py
功能说明:三点法制导律参数影响分析主程序
版本号：1.0
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
    KC_VALUES,
    KD_VALUES,
    KE_VALUES,
    MAX_OVERLOAD_G,
    METRIC_PNG,
    MISSILE_POSITION_M,
    MISSILE_VELOCITY_MPS,
    SAVE_DIR,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TABLE_DIR,
    TARGET_POSITION_M,
    TARGET_VELOCITY_MPS,
    TITLE,
    T_MAX_S,
    ensure_directories,
)

G0 = 9.80665


def configure_matplotlib() -> None:
    """
    功能：设置中文字体与坐标轴负号显示。
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
    功能：保存实验汇总结果。
    参数：rows 为结果字典列表。
    返回：无。
    调用位置：main() 结束前。
    """

    with open(SUMMARY_CSV, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(SUMMARY_JSON, "w", encoding="utf-8") as handle:
        json.dump({"title": TITLE, "results": rows}, handle, ensure_ascii=False, indent=2)


def plot_metrics(grouped_rows: dict[str, list[dict]]) -> None:
    """
    功能：绘制三类增益扫描对应的过载和脱靶量变化图。
    参数：grouped_rows 为按增益类别分组的结果字典。
    返回：无。
    调用位置：main() 计算完成后。
    """

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=False)
    for axis, key in zip(axes, ("k_e", "k_d", "k_c")):
        rows = grouped_rows[key]
        axis.plot([item["gain_value"] for item in rows], [item["max_required_overload_g"] for item in rows], marker="o", label="最大需用过载")
        axis.plot([item["gain_value"] for item in rows], [item["miss_distance_m"] for item in rows], marker="s", label="脱靶量")
        axis.set_title(key)
        axis.set_xlabel(f"{key} 增益")
        axis.grid(True, linestyle="--", alpha=0.4)
        axis.legend()
    fig.tight_layout()
    fig.savefig(METRIC_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行三点法实验一的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    results = []

    for gain_name, gain_values in (("k_e", KE_VALUES), ("k_d", KD_VALUES), ("k_c", KC_VALUES)):
        for gain_value in gain_values:
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
            flight_time_s = 0.0
            intercepted = False

            if gain_name == "k_e":
                k_e = gain_value
                k_d = BASELINE_KD
                k_c = BASELINE_KC
            elif gain_name == "k_d":
                k_e = BASELINE_KE
                k_d = gain_value
                k_c = BASELINE_KC
            else:
                k_e = BASELINE_KE
                k_d = BASELINE_KD
                k_c = gain_value

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
                    k_e * line_error / station_range_t
                    + k_d * line_error_rate / max(missile_speed_mps, 1.0)
                    + k_c * theta_ref_dot
                )
                required_g = missile_speed_mps * gamma_dot_cmd / G0
                actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))

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

            results.append(
                {
                    "gain_name": gain_name,
                    "gain_value": gain_value,
                    "max_required_overload_g": round(max_required_g, 6),
                    "miss_distance_m": round(min_range, 6),
                    "intercepted": intercepted,
                    "flight_time_s": round(flight_time_s, 6),
                }
            )

    grouped_rows = {
        "k_e": [item for item in results if item["gain_name"] == "k_e"],
        "k_d": [item for item in results if item["gain_name"] == "k_d"],
        "k_c": [item for item in results if item["gain_name"] == "k_c"],
    }

    write_summary(results)
    # 绘制三类增益扫描的统计曲线。
    plot_metrics(grouped_rows)
    print(f"实验完成，结果已保存到: {SAVE_DIR}")


if __name__ == "__main__":
    main()
