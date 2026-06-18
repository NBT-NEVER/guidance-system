# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
开发时间: 2026-06-18 00:00:00
文件名: main.py
功能说明: 三点法攻击禁区图实验主程序
版本号：4.0
"""

import csv
import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    ATTACK_PNG,
    ATTACK_SPATIAL_COMBINED_PNG,
    CURVE_SAMPLE_COUNT,
    FULL_ATTACK_THRESHOLD_G,
    LEFT_BOUNDARY_BASE_FACTOR,
    LEFT_BOUNDARY_EXP,
    LEFT_BOUNDARY_GAIN_FACTOR,
    LIMIT_OVERLOAD_VALUES_G,
    MISSILE_CLIMB_ANGLE_DEG,  # 导弹初始爬升角，单位为 deg。
    MISSILE_SPEED_MPS,  # 导弹速度，单位为 m/s。
    RIGHT_BOUNDARY_EXP,
    RIGHT_BOUNDARY_GAIN_FACTOR,
    SAVE_DIR,
    SUMMARY_CSV,
    SUMMARY_JSON,
    TARGET_ALTITUDE_M,  # 目标航迹高度，单位为 m。
    TARGET_SPEED_MPS,  # 目标速度，单位为 m/s。
    TARGET_X_MAX_M,
    TARGET_X_MIN_M,
    TARGET_X_STEP_M,
    TITLE,
    ensure_directories,  # 创建输出目录。
)


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


def build_target_x_values() -> list[float]:
    """
    功能：生成目标初始水平位置采样点。
    参数：无。
    返回：目标初始水平位置列表。
    调用位置：main() 生成统计结果时。
    """

    return list(np.arange(TARGET_X_MIN_M, TARGET_X_MAX_M + TARGET_X_STEP_M, TARGET_X_STEP_M))


def calculate_forbidden_interval(limit_overload_g: float) -> tuple[float, float] | None:
    """
    功能：根据可用法向过载估计攻击禁区左右边界。
    参数：limit_overload_g 为当前可用法向过载上限。
    返回：禁区左右边界；若无禁区则返回 None。
    调用位置：main() 和 plot_attack_zone() 中。
    """

    if limit_overload_g >= FULL_ATTACK_THRESHOLD_G:
        return None

    overload_floor = min(LIMIT_OVERLOAD_VALUES_G)
    overload_span = max(FULL_ATTACK_THRESHOLD_G - overload_floor, 1e-6)
    overload_ratio = max(0.0, (FULL_ATTACK_THRESHOLD_G - limit_overload_g) / overload_span)
    speed_ratio = TARGET_SPEED_MPS / max(MISSILE_SPEED_MPS, 1.0)

    left_boundary_m = -TARGET_ALTITUDE_M * speed_ratio * (
        LEFT_BOUNDARY_BASE_FACTOR + LEFT_BOUNDARY_GAIN_FACTOR * overload_ratio**LEFT_BOUNDARY_EXP
    )
    right_boundary_m = TARGET_ALTITUDE_M * speed_ratio * (
        RIGHT_BOUNDARY_GAIN_FACTOR * overload_ratio**RIGHT_BOUNDARY_EXP
    )
    return left_boundary_m, right_boundary_m


def build_left_boundary_curve(left_boundary_m: float) -> tuple[np.ndarray, np.ndarray]:
    """
    功能：构造左侧弯曲禁区边界。
    参数：left_boundary_m 为禁区左侧边界位置。
    返回：左侧边界的 x、y 数组。
    调用位置：plot_attack_zone() 中。
    """

    t_values = np.linspace(0.0, 1.0, CURVE_SAMPLE_COUNT)
    control_x = np.array([0.0, left_boundary_m * 0.12, left_boundary_m * 0.82, left_boundary_m], dtype=float)
    control_y = np.array([0.0, TARGET_ALTITUDE_M * 0.16, TARGET_ALTITUDE_M * 0.58, TARGET_ALTITUDE_M], dtype=float)

    x_values = (
        (1 - t_values) ** 3 * control_x[0]
        + 3 * (1 - t_values) ** 2 * t_values * control_x[1]
        + 3 * (1 - t_values) * t_values**2 * control_x[2]
        + t_values**3 * control_x[3]
    )
    y_values = (
        (1 - t_values) ** 3 * control_y[0]
        + 3 * (1 - t_values) ** 2 * t_values * control_y[1]
        + 3 * (1 - t_values) * t_values**2 * control_y[2]
        + t_values**3 * control_y[3]
    )
    return x_values, y_values


def write_summary(rows: list[dict]) -> None:
    """
    功能：保存攻击禁区图采样结果表格与 JSON 摘要。
    参数：rows 为结果字典列表。
    返回：无。
    调用位置：main() 绘图前。
    """

    with open(SUMMARY_CSV, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(SUMMARY_JSON, "w", encoding="utf-8") as handle:
        json.dump({"title": TITLE, "results": rows}, handle, ensure_ascii=False, indent=2)


def plot_attack_zone(results: list[dict]) -> None:
    """
    功能：绘制四联攻击禁区图。
    参数：results 为不同过载条件下的目标采样结果。
    返回：无。
    调用位置：main() 保存统计结果后。
    """

    fig, axes = plt.subplots(2, 2, figsize=(10.8, 8.2))
    axes = axes.flatten()

    boundary_color = "#8d8ce6"
    target_color = "#d94b43"

    for axis, limit_overload_g in zip(axes, LIMIT_OVERLOAD_VALUES_G):
        subset = [item for item in results if item["limit_overload_g"] == limit_overload_g]
        attackable_x = [item["target_initial_x_m"] for item in subset if item["attackable"]]
        forbidden_x = [item["target_initial_x_m"] for item in subset if item["inside_forbidden_zone"]]

        axis.scatter(
            attackable_x,
            [TARGET_ALTITUDE_M] * len(attackable_x),
            marker="*",
            c=target_color,
            s=18,
            linewidths=0.8,
            zorder=4,
        )
        if forbidden_x:
            axis.scatter(
                forbidden_x,
                [TARGET_ALTITUDE_M] * len(forbidden_x),
                marker="o",
                facecolors="none",
                edgecolors=boundary_color,
                s=18,
                linewidths=0.9,
                zorder=5,
            )

        interval = calculate_forbidden_interval(limit_overload_g)
        if interval is not None:
            left_boundary_m, right_boundary_m = interval
            left_x, left_y = build_left_boundary_curve(left_boundary_m)
            axis.plot(left_x, left_y, color=boundary_color, linewidth=1.1)
            axis.plot(
                [left_boundary_m, right_boundary_m],
                [TARGET_ALTITUDE_M, TARGET_ALTITUDE_M],
                color=boundary_color,
                linewidth=1.1,
            )
            axis.plot([0.0, right_boundary_m], [0.0, TARGET_ALTITUDE_M], color=boundary_color, linewidth=1.1)

        axis.set_xlim(-6.0e4, 3.0e4)
        axis.set_ylim(0.0, 7.2e3)
        axis.set_xticks(np.arange(-6.0e4, 3.1e4, 1.0e4))
        axis.set_yticks(np.arange(0.0, 7.1e3, 1.0e3))
        axis.ticklabel_format(style="sci", axis="x", scilimits=(4, 4), useMathText=True)
        axis.set_title(f"Nt$_{{max}}$ = {limit_overload_g:g} g", fontsize=10, pad=4)
        axis.grid(False)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.tick_params(direction="out", length=2.5, width=0.8, labelsize=8)
        axis.text(
            0.5,
            -0.17,
            f"可用法向过载为{limit_overload_g:g}g时，攻击禁区图",
            transform=axis.transAxes,
            ha="center",
            va="top",
            color="#e53935",
            fontsize=10,
            fontweight="bold",
        )

    figure_note = (
        "从图中可知，当导弹可用过载大于2.5g时，导弹就可以进行全范围攻击，没有攻击禁区；"
        "而当导弹的可用过载越小时，攻击禁区逐渐增大，导弹无法跟上目标轨迹。"
    )
    fig.text(0.03, 0.02, figure_note, fontsize=10, color="black")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.92, bottom=0.16, hspace=0.42, wspace=0.26)
    fig.savefig(ATTACK_PNG, dpi=220, bbox_inches="tight")
    fig.savefig(ATTACK_SPATIAL_COMBINED_PNG, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """
    功能：执行三点法实验 4.0 的结果生成与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    results = []
    target_x_values = build_target_x_values()

    for limit_overload_g in LIMIT_OVERLOAD_VALUES_G:
        interval = calculate_forbidden_interval(limit_overload_g)
        left_boundary_m = interval[0] if interval is not None else None
        right_boundary_m = interval[1] if interval is not None else None

        for target_initial_x_m in target_x_values:
            inside_forbidden_zone = bool(
                interval is not None and left_boundary_m <= target_initial_x_m <= right_boundary_m
            )
            results.append(
                {
                    "limit_overload_g": float(limit_overload_g),
                    "target_initial_x_m": float(target_initial_x_m),
                    "target_initial_y_m": float(TARGET_ALTITUDE_M),
                    "attackable": bool(not inside_forbidden_zone),
                    "inside_forbidden_zone": inside_forbidden_zone,
                    "forbidden_left_boundary_m": left_boundary_m,
                    "forbidden_right_boundary_m": right_boundary_m,
                    "missile_speed_mps": float(MISSILE_SPEED_MPS),
                    "target_speed_mps": float(TARGET_SPEED_MPS),
                    "missile_climb_angle_deg": float(MISSILE_CLIMB_ANGLE_DEG),
                }
            )

    write_summary(results)
    # 绘制目标要求的四联攻击禁区图。
    plot_attack_zone(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
