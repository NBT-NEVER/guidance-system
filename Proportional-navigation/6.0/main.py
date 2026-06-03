# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: main.py
生成时间: 2026-06-03 15:59:50
文件名: main.py
功能说明: 比例导引实验主程序 / Main entry for proportional-navigation experiment.
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

from config import build_config, ensure_directories

G0 = 9.80665

available_fonts = {item.name for item in font_manager.fontManager.ttflist}
for font_name in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "WenQuanYi Micro Hei", "Arial Unicode MS"):
    if font_name in available_fonts:
        plt.rcParams["font.sans-serif"] = [font_name, *plt.rcParams.get("font.sans-serif", [])]
        break
plt.rcParams["axes.unicode_minus"] = False


def wrap_to_pi(angle: float) -> float:
    """
    功能：将角度限制在 [-pi, pi]，保证视线角和弹道倾角变化连续。
    参数：angle 为待处理角度，单位 rad。
    返回：限制后的角度，单位 rad。
    调用位置：run_png_case() 及姿态回路的角度更新计算。
    """

    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def write_rows(rows: list[dict], file_path) -> None:
    """
    功能：把比例导引实验统计结果写入 UTF-8 CSV 文件。
    参数：rows 为结果字典列表，file_path 为输出路径。
    返回：无。
    调用位置：main() 在不同实验模式结束后统一调用。
    """

    if not rows:
        return
    with open(file_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_json(payload: dict, file_path) -> None:
    """
    功能：保存结构化实验摘要，便于后续复现实验和复查参数。
    参数：payload 为可序列化字典，file_path 为输出路径。
    返回：无。
    调用位置：main() 导出 summary.json 时调用。
    """

    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def run_png_case(
    case_name: str,
    navigation_ratio: float,
    missile_speed_mps: float,
    target_speed_mps: float,
    missile_position: tuple[float, float],
    target_position: tuple[float, float],
    target_heading_deg: float,
    max_overload_g: float,
    dt: float,
    t_max_s: float,
    hit_radius_m: float,
    target_normal_g: float = 0.0,
    noise_std_radps: float = 0.0,
    enable_attitude_loop: bool = False,
    zeta: float = 0.707,
    omega_n: float = 10.0,
    seed: int = 20260603,
) -> dict:
    """
    功能：对单个比例导引工况进行数值积分，输出脱靶量、过载与完整轨迹。
    参数：包含导航比、初始阵位、目标机动、噪声和姿态回路等单工况设置。
    返回：含指标统计和轨迹时程的结果字典。
    调用位置：main() 中的导航比扫描、噪声实验、目标机动实验和攻击区实验。
    """

    rng = np.random.default_rng(seed)
    x_m, y_m = missile_position
    x_t, y_t = target_position
    gamma = math.atan2(y_t - y_m, x_t - x_m)
    target_heading = math.radians(target_heading_deg)
    overload_state_g = 0.0
    overload_rate_g = 0.0
    min_range = math.hypot(x_t - x_m, y_t - y_m)
    max_required_g = 0.0
    max_actual_g = 0.0
    saturation_steps = 0
    flight_time_s = 0.0
    intercepted = False
    time_history = []
    required_history = []
    actual_history = []
    missile_x = [x_m]
    missile_y = [y_m]
    target_x = [x_t]
    target_y = [y_t]

    for step in range(int(t_max_s / dt)):
        vx_m = missile_speed_mps * math.cos(gamma)
        vy_m = missile_speed_mps * math.sin(gamma)
        vx_t = target_speed_mps * math.cos(target_heading)
        vy_t = target_speed_mps * math.sin(target_heading)

        rel_x = x_t - x_m
        rel_y = y_t - y_m
        rel_range = math.hypot(rel_x, rel_y)
        min_range = min(min_range, rel_range)
        if rel_range <= hit_radius_m:
            intercepted = True
            flight_time_s = step * dt
            break

        rel_vx = vx_t - vx_m
        rel_vy = vy_t - vy_m
        los_rate = (rel_x * rel_vy - rel_y * rel_vx) / max(rel_range**2, 1.0)
        closing_speed = -(rel_x * rel_vx + rel_y * rel_vy) / max(rel_range, 1.0)
        measured_los_rate = los_rate + rng.normal(0.0, noise_std_radps)
        required_g = navigation_ratio * max(closing_speed, 0.0) * measured_los_rate / G0
        limited_g = max(-max_overload_g, min(max_overload_g, required_g))
        if abs(required_g) > max_overload_g:
            saturation_steps += 1

        if enable_attitude_loop:
            overload_ddot = omega_n**2 * (limited_g - overload_state_g) - 2.0 * zeta * omega_n * overload_rate_g
            overload_rate_g += overload_ddot * dt
            overload_state_g += overload_rate_g * dt
            actual_g = max(-max_overload_g, min(max_overload_g, overload_state_g))
        else:
            actual_g = limited_g

        gamma += actual_g * G0 / missile_speed_mps * dt
        if target_normal_g != 0.0:
            target_heading += target_normal_g * G0 / target_speed_mps * dt

        x_m += missile_speed_mps * math.cos(gamma) * dt
        y_m += missile_speed_mps * math.sin(gamma) * dt
        x_t += target_speed_mps * math.cos(target_heading) * dt
        y_t += target_speed_mps * math.sin(target_heading) * dt
        max_required_g = max(max_required_g, abs(required_g))
        max_actual_g = max(max_actual_g, abs(actual_g))
        time_history.append(step * dt)
        required_history.append(required_g)
        actual_history.append(actual_g)
        missile_x.append(x_m)
        missile_y.append(y_m)
        target_x.append(x_t)
        target_y.append(y_t)
        flight_time_s = step * dt

        if step > 20 and closing_speed < 0.0 and rel_range > min_range + 1.0:
            break

    return {
        "case_name": case_name,
        "navigation_ratio": round(navigation_ratio, 6),
        "missile_speed_mps": round(missile_speed_mps, 3),
        "target_speed_mps": round(target_speed_mps, 3),
        "max_required_overload_g": round(max_required_g, 6),
        "max_actual_overload_g": round(max_actual_g, 6),
        "miss_distance_m": round(min_range, 6),
        "intercepted": intercepted,
        "flight_time_s": round(flight_time_s, 6),
        "noise_std_radps": round(noise_std_radps, 9),
        "target_normal_g": round(target_normal_g, 6),
        "saturation_ratio": round(saturation_steps / max(1, len(time_history)), 6),
        "trajectory": {
            "missile_x": missile_x,
            "missile_y": missile_y,
            "target_x": target_x,
            "target_y": target_y,
            "time_s": time_history,
            "required_g": required_history,
            "actual_g": actual_history,
        },
    }


def render_traj_and_metrics(results: list[dict], x_key: str, x_label: str, cfg: dict) -> None:
    """
    功能：为比例导引扫描类实验绘制弹道对比图和指标曲线图。
    参数：results 为工况结果列表，x_key 为横轴字段名，x_label 为横轴中文标签。
    返回：无。
    调用位置：main() 中的实验 1、3、4 和姿态回路对比图保存阶段。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    for item in results:
        traj = item["trajectory"]
        ax.plot(traj["missile_x"], traj["missile_y"], label=f"{x_label}={item[x_key]}")
    if results:
        target_traj = results[0]["trajectory"]
        ax.plot(target_traj["target_x"], target_traj["target_y"], linestyle="--", color="black", label="目标")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(cfg["title"])
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(cfg["trajectory_png"], dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    axes[0].plot([item[x_key] for item in results], [item["max_required_overload_g"] for item in results], marker="o")
    axes[0].axhline(cfg["max_overload_g"], color="red", linestyle="--", label="可用过载上限")
    axes[0].set_ylabel("最大需用过载 / g")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[1].plot([item[x_key] for item in results], [item["miss_distance_m"] for item in results], marker="s", color="#b54d1a")
    axes[1].set_xlabel(x_label)
    axes[1].set_ylabel("脱靶量 / m")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(cfg["metric_png"], dpi=200)
    plt.close(fig)


def render_noise_plot(results: list[dict], cfg: dict) -> None:
    """
    功能：把导航比与白噪声水平的组合结果绘成双指标折线图。
    参数：results 为所有 K 和噪声标准差组合的结果列表，cfg 为配置字典。
    返回：无。
    调用位置：main() 的导航比噪声实验分支。
    """

    grouped = {}
    for item in results:
        grouped.setdefault(item["navigation_ratio"], []).append(item)
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    for nav_ratio, items in grouped.items():
        items = sorted(items, key=lambda row: row["noise_std_radps"])
        x_axis = [row["noise_std_radps"] for row in items]
        axes[0].plot(x_axis, [row["max_required_overload_g"] for row in items], marker="o", label=f"K={nav_ratio}")
        axes[1].plot(x_axis, [row["miss_distance_m"] for row in items], marker="s", label=f"K={nav_ratio}")
    axes[0].set_ylabel("最大需用过载 / g")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()
    axes[1].set_xlabel("视线角速率白噪声标准差 / rad/s")
    axes[1].set_ylabel("脱靶量 / m")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(cfg["metric_png"], dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    for item in sorted(results, key=lambda row: (row["navigation_ratio"], row["noise_std_radps"])):
        traj = item["trajectory"]
        label = f"K={item['navigation_ratio']},σ={item['noise_std_radps']:.4f}"
        ax.plot(traj["missile_x"], traj["missile_y"], label=label)
    target_traj = results[0]["trajectory"]
    ax.plot(target_traj["target_x"], target_traj["target_y"], linestyle="--", color="black", label="目标")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(cfg["title"])
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(cfg["trajectory_png"], dpi=200)
    plt.close(fig)


def render_attack_zone(results: list[dict], cfg: dict) -> None:
    """
    功能：把比例导引允许攻击区扫描结果绘成极坐标展开后的二维散点图。
    参数：results 为不同发射点工况的仿真结果，cfg 为配置字典。
    返回：无。
    调用位置：main() 在实验 5 中完成扫描后绘图。
    """

    success_x = []
    success_y = []
    fail_x = []
    fail_y = []
    for item in results:
        radius = item["launch_radius_m"]
        angle = math.radians(item["launch_angle_deg"])
        x_pos = radius * math.cos(angle)
        y_pos = radius * math.sin(angle)
        feasible = item["intercepted"] and item["miss_distance_m"] < cfg["hit_radius_m"] and item["max_required_overload_g"] <= cfg["max_overload_g"]
        if feasible:
            success_x.append(x_pos)
            success_y.append(y_pos)
        else:
            fail_x.append(x_pos)
            fail_y.append(y_pos)

    fig, ax = plt.subplots(figsize=(9, 6))
    if success_x:
        ax.scatter(success_x, success_y, s=14, c="#2d8c4d", label="允许攻击区")
    if fail_x:
        ax.scatter(fail_x, fail_y, s=14, c="#c24b37", label="攻击禁区")
    ax.set_xlabel("导弹发射点 x / m")
    ax.set_ylabel("导弹发射点 y / m")
    ax.set_title(cfg["title"])
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(cfg["attack_png"], dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：根据 config.py 中的实验模式执行比例导引仿真并导出图表与统计表。
    参数：无。
    返回：无。
    调用位置：python main.py 程序入口。
    """

    ensure_directories()
    cfg = build_config()
    mode = cfg["mode"]
    results = []

    if mode == "navigation_ratio_sweep":
        base = cfg["base_scenario"]
        for nav_ratio in cfg["navigation_ratio_values"]:
            case = run_png_case(
                case_name=f"K={nav_ratio}",
                navigation_ratio=nav_ratio,
                missile_speed_mps=base["missile_speed_mps"],
                target_speed_mps=base["target_speed_mps"],
                missile_position=tuple(base["missile_position_m"]),
                target_position=tuple(base["target_position_m"]),
                target_heading_deg=base["target_heading_deg"],
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            results.append(case)
        render_traj_and_metrics(results, "navigation_ratio", "导航比 K", cfg)

    elif mode == "noise_sweep":
        base = cfg["base_scenario"]
        baseline = run_png_case(
            case_name="baseline",
            navigation_ratio=cfg["navigation_ratio_values"][0],
            missile_speed_mps=base["missile_speed_mps"],
            target_speed_mps=base["target_speed_mps"],
            missile_position=tuple(base["missile_position_m"]),
            target_position=tuple(base["target_position_m"]),
            target_heading_deg=base["target_heading_deg"],
            max_overload_g=cfg["max_overload_g"],
            dt=cfg["dt"],
            t_max_s=cfg["t_max_s"],
            hit_radius_m=cfg["hit_radius_m"],
        )
        first_traj = baseline["trajectory"]
        rel_x0 = first_traj["target_x"][0] - first_traj["missile_x"][0]
        rel_y0 = first_traj["target_y"][0] - first_traj["missile_y"][0]
        initial_gamma = math.atan2(rel_y0, rel_x0)
        vx_m = base["missile_speed_mps"] * math.cos(initial_gamma)
        vy_m = base["missile_speed_mps"] * math.sin(initial_gamma)
        vx_t = base["target_speed_mps"] * math.cos(math.radians(base["target_heading_deg"]))
        vy_t = base["target_speed_mps"] * math.sin(math.radians(base["target_heading_deg"]))
        los_rate0 = (rel_x0 * (vy_t - vy_m) - rel_y0 * (vx_t - vx_m)) / max(rel_x0**2 + rel_y0**2, 1.0)
        for nav_ratio in cfg["navigation_ratio_values"]:
            for divisor in cfg["noise_divisors"]:
                case = run_png_case(
                    case_name=f"K={nav_ratio},1/{divisor}",
                    navigation_ratio=nav_ratio,
                    missile_speed_mps=base["missile_speed_mps"],
                    target_speed_mps=base["target_speed_mps"],
                    missile_position=tuple(base["missile_position_m"]),
                    target_position=tuple(base["target_position_m"]),
                    target_heading_deg=base["target_heading_deg"],
                    max_overload_g=cfg["max_overload_g"],
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                    noise_std_radps=abs(los_rate0) / divisor,
                    seed=20260603 + int(nav_ratio * 100) + divisor,
                )
                case["noise_divisor"] = divisor
                results.append(case)
        render_noise_plot(results, cfg)

    elif mode == "minimum_navigation_ratio":
        base = cfg["base_scenario"]
        for speed_ratio in cfg["speed_ratio_values"]:
            missile_speed = speed_ratio * base["target_speed_mps"]
            found_value = None
            for nav_ratio in np.arange(cfg["search_range"]["start"], cfg["search_range"]["stop"] + cfg["search_range"]["step"] / 2.0, cfg["search_range"]["step"]):
                case = run_png_case(
                    case_name=f"P={speed_ratio},K={nav_ratio:.1f}",
                    navigation_ratio=float(round(nav_ratio, 1)),
                    missile_speed_mps=missile_speed,
                    target_speed_mps=base["target_speed_mps"],
                    missile_position=tuple(base["missile_position_m"]),
                    target_position=tuple(base["target_position_m"]),
                    target_heading_deg=base["target_heading_deg"],
                    max_overload_g=cfg["max_overload_g"],
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                )
                if case["intercepted"] and case["miss_distance_m"] < cfg["convergence_threshold_m"]:
                    found_value = round(float(nav_ratio), 1)
                    break
            results.append(
                {
                    "case_name": f"P={speed_ratio}",
                    "navigation_ratio": found_value,
                    "speed_ratio": speed_ratio,
                    "missile_speed_mps": round(missile_speed, 3),
                    "target_speed_mps": round(base["target_speed_mps"], 3),
                    "max_required_overload_g": "",
                    "max_actual_overload_g": "",
                    "miss_distance_m": "",
                    "intercepted": found_value is not None,
                    "flight_time_s": "",
                    "noise_std_radps": "",
                    "target_normal_g": "",
                    "saturation_ratio": "",
                }
            )
        fig, ax = plt.subplots(figsize=(9, 6))
        x_values = [item["speed_ratio"] for item in results]
        y_values = [np.nan if item["navigation_ratio"] is None else item["navigation_ratio"] for item in results]
        ax.plot(x_values, y_values, marker="o")
        ax.set_xlabel("弹目速度比 P")
        ax.set_ylabel("最小导航比 Kmin")
        ax.set_title(cfg["title"])
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()
        fig.savefig(cfg["metric_png"], dpi=200)
        plt.close(fig)

    elif mode == "target_maneuver_sweep":
        base = cfg["base_scenario"]
        for target_normal_g in cfg["target_normal_g_values"]:
            case = run_png_case(
                case_name=f"Nt={target_normal_g}",
                navigation_ratio=cfg["navigation_ratio"],
                missile_speed_mps=base["missile_speed_mps"],
                target_speed_mps=base["target_speed_mps"],
                missile_position=tuple(base["missile_position_m"]),
                target_position=tuple(base["target_position_m"]),
                target_heading_deg=base["target_heading_deg"],
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
                target_normal_g=target_normal_g,
            )
            results.append(case)
        render_traj_and_metrics(results, "target_normal_g", "目标机动过载 / g", cfg)

    elif mode == "attack_zone":
        base = cfg["base_scenario"]
        for radius in cfg["launch_scan"]["radius_values_m"]:
            for angle_deg in cfg["launch_scan"]["angle_values_deg"]:
                missile_position = (radius * math.cos(math.radians(angle_deg)), radius * math.sin(math.radians(angle_deg)))
                case = run_png_case(
                    case_name=f"r={radius},q={angle_deg}",
                    navigation_ratio=cfg["navigation_ratio"],
                    missile_speed_mps=base["missile_speed_mps"],
                    target_speed_mps=base["target_speed_mps"],
                    missile_position=missile_position,
                    target_position=tuple(base["target_position_m"]),
                    target_heading_deg=base["target_heading_deg"],
                    max_overload_g=cfg["max_overload_g"],
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                )
                case["launch_radius_m"] = radius
                case["launch_angle_deg"] = angle_deg
                results.append(case)
        render_attack_zone(results, cfg)

    elif mode == "attitude_compare":
        base = cfg["base_scenario"]
        ideal_case = run_png_case(
            case_name="无姿态回路",
            navigation_ratio=cfg["navigation_ratio"],
            missile_speed_mps=base["missile_speed_mps"],
            target_speed_mps=base["target_speed_mps"],
            missile_position=tuple(base["missile_position_m"]),
            target_position=tuple(base["target_position_m"]),
            target_heading_deg=base["target_heading_deg"],
            max_overload_g=cfg["max_overload_g"],
            dt=cfg["dt"],
            t_max_s=cfg["t_max_s"],
            hit_radius_m=cfg["hit_radius_m"],
        )
        loop_case = run_png_case(
            case_name="二阶姿态回路",
            navigation_ratio=cfg["navigation_ratio"],
            missile_speed_mps=base["missile_speed_mps"],
            target_speed_mps=base["target_speed_mps"],
            missile_position=tuple(base["missile_position_m"]),
            target_position=tuple(base["target_position_m"]),
            target_heading_deg=base["target_heading_deg"],
            max_overload_g=cfg["max_overload_g"],
            dt=cfg["dt"],
            t_max_s=cfg["t_max_s"],
            hit_radius_m=cfg["hit_radius_m"],
            enable_attitude_loop=True,
            zeta=cfg["attitude_loop"]["zeta"],
            omega_n=cfg["attitude_loop"]["omega_n"],
        )
        results = [ideal_case, loop_case]
        render_traj_and_metrics(results, "navigation_ratio", "导航比 K", cfg)

    else:
        raise ValueError(f"未支持的实验模式: {mode}")

    summary_rows = []
    for item in results:
        summary_rows.append({key: value for key, value in item.items() if key != "trajectory"})
    write_rows(summary_rows, cfg["summary_csv"])
    save_json({"title": cfg["title"], "mode": mode, "results": summary_rows}, cfg["detail_json"])
    print(f"实验完成，结果已保存到: {cfg['save_dir']}")


if __name__ == "__main__":
    main()
