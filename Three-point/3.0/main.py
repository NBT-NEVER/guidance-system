# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: main.py
生成时间: 2026-06-03 15:59:50
文件名: main.py
功能说明: 三点法与前置量法实验主程序 / Main entry for three-point guidance experiment.
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
    功能：将角度限制在 [-pi, pi]，保证三点法和前置量法的角度更新连续。
    参数：angle 为待处理角度，单位 rad。
    返回：限制后的角度，单位 rad。
    调用位置：run_remote_case() 计算导引参考线和导弹姿态误差时调用。
    """

    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def write_rows(rows: list[dict], file_path) -> None:
    """
    功能：把遥控制导实验的统计结果写入 CSV 表格。
    参数：rows 为结果字典列表，file_path 为输出路径。
    返回：无。
    调用位置：main() 在各个实验分支完成后统一调用。
    """

    if not rows:
        return
    with open(file_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_json(payload: dict, file_path) -> None:
    """
    功能：保存实验摘要 JSON，便于后续对照三点法参数和发射阵位。
    参数：payload 为可序列化字典，file_path 为输出路径。
    返回：无。
    调用位置：main() 在导出统计结果后同步写入。
    """

    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def run_remote_case(
    case_name: str,
    law_name: str,
    lead_factor: float,
    gains: dict,
    missile_position: tuple[float, float],
    target_position: tuple[float, float],
    missile_velocity: tuple[float, float],
    target_velocity: tuple[float, float],
    max_overload_g: float,
    dt: float,
    t_max_s: float,
    hit_radius_m: float,
    target_normal_g: float = 0.0,
    enable_attitude_loop: bool = False,
    zeta: float = 0.707,
    omega_n: float = 10.0,
) -> dict:
    """
    功能：执行单个三点法、前置量法或半前置量法工况的数值积分。
    参数：包含初始阵位、速度矢量、增益、前置系数、机动过载和姿态回路设置。
    返回：含最大需用过载、脱靶量、命中标记和轨迹时程的结果字典。
    调用位置：main() 在参数扫描、方法对比、攻击禁区和姿态回路实验中调用。
    """

    x_m, y_m = missile_position
    x_t, y_t = target_position
    missile_speed_mps = math.hypot(*missile_velocity)
    target_speed_mps = math.hypot(*target_velocity)
    gamma = math.atan2(missile_velocity[1], missile_velocity[0])
    target_heading = math.atan2(target_velocity[1], target_velocity[0])
    overload_state_g = 0.0
    overload_rate_g = 0.0
    prev_line_error = 0.0
    prev_ref_angle = math.atan2(y_t, x_t) if (x_t != 0.0 or y_t != 0.0) else 0.0
    min_range = math.hypot(x_t - x_m, y_t - y_m)
    max_required_g = 0.0
    max_actual_g = 0.0
    terminal_g = 0.0
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
        range_mt = math.hypot(x_t - x_m, y_t - y_m)
        min_range = min(min_range, range_mt)
        if range_mt <= hit_radius_m:
            intercepted = True
            flight_time_s = step * dt
            break

        station_range_t = max(math.hypot(x_t, y_t), 1.0)
        theta_t = math.atan2(y_t, x_t)
        target_los_rate = (x_t * vy_t - y_t * vx_t) / max(x_t**2 + y_t**2, 1.0)
        rel_vx = vx_t - vx_m
        rel_vy = vy_t - vy_m
        closing_speed = -((x_t - x_m) * rel_vx + (y_t - y_m) * rel_vy) / max(range_mt, 1.0)
        t_go = range_mt / max(closing_speed, 1.0)
        theta_ref = theta_t + lead_factor * target_los_rate * t_go
        theta_ref_dot = wrap_to_pi(theta_ref - prev_ref_angle) / dt
        line_error = x_m * math.sin(theta_ref) - y_m * math.cos(theta_ref)
        line_error_rate = (line_error - prev_line_error) / dt
        gamma_dot_cmd = -(
            gains["k_e"] * line_error / station_range_t
            + gains["k_d"] * line_error_rate / max(missile_speed_mps, 1.0)
            + gains["k_c"] * theta_ref_dot
        )
        required_g = missile_speed_mps * gamma_dot_cmd / G0
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
        prev_line_error = line_error
        prev_ref_angle = theta_ref
        max_required_g = max(max_required_g, abs(required_g))
        max_actual_g = max(max_actual_g, abs(actual_g))
        terminal_g = actual_g
        time_history.append(step * dt)
        required_history.append(required_g)
        actual_history.append(actual_g)
        missile_x.append(x_m)
        missile_y.append(y_m)
        target_x.append(x_t)
        target_y.append(y_t)
        flight_time_s = step * dt

        if step > 20 and closing_speed < 0.0 and range_mt > min_range + 1.0:
            break

    return {
        "case_name": case_name,
        "law_name": law_name,
        "lead_factor": lead_factor,
        "max_required_overload_g": round(max_required_g, 6),
        "max_actual_overload_g": round(max_actual_g, 6),
        "terminal_overload_g": round(abs(terminal_g), 6),
        "miss_distance_m": round(min_range, 6),
        "intercepted": intercepted,
        "flight_time_s": round(flight_time_s, 6),
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


def render_curve_bundle(results: list[dict], x_key: str, x_label: str, title: str, cfg: dict) -> None:
    """
    功能：为三点法增益扫描和机动扫描实验绘制指标曲线。
    参数：results 为结果列表，x_key 为横轴字段名，x_label 为横轴中文名，title 为图题。
    返回：无。
    调用位置：main() 的参数扫描和目标机动实验分支。
    """

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    axes[0].plot([item[x_key] for item in results], [item["max_required_overload_g"] for item in results], marker="o")
    axes[0].set_ylabel("最大需用过载 / g")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[1].plot([item[x_key] for item in results], [item["miss_distance_m"] for item in results], marker="s", color="#b54d1a")
    axes[1].set_xlabel(x_label)
    axes[1].set_ylabel("脱靶量 / m")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(cfg["metric_png"], dpi=200)
    plt.close(fig)


def render_method_compare(results: list[dict], group_key: str, cfg: dict) -> None:
    """
    功能：为三点法、前置量法和半前置量法对比实验绘制分组折线图。
    参数：results 为结果列表，group_key 为分类字段，cfg 为配置字典。
    返回：无。
    调用位置：main() 的方法对比实验分支。
    """

    grouped = {}
    for item in results:
        grouped.setdefault(item["law_name"], []).append(item)
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    for law_name, items in grouped.items():
        items = sorted(items, key=lambda row: row[group_key])
        x_values = [row[group_key] for row in items]
        axes[0].plot(x_values, [row["max_required_overload_g"] for row in items], marker="o", label=law_name)
        axes[1].plot(x_values, [row["terminal_overload_g"] for row in items], marker="s", label=law_name)
        axes[2].plot(x_values, [row["miss_distance_m"] for row in items], marker="^", label=law_name)
    axes[0].set_ylabel("最大需用过载 / g")
    axes[1].set_ylabel("命中点过载 / g")
    axes[2].set_ylabel("脱靶量 / m")
    axes[2].set_xlabel(group_key)
    for axis in axes:
        axis.grid(True, linestyle="--", alpha=0.4)
        axis.legend()
    fig.tight_layout()
    fig.savefig(cfg["metric_png"], dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6))
    for item in results:
        if item[group_key] == sorted({row[group_key] for row in results})[0]:
            traj = item["trajectory"]
            ax.plot(traj["missile_x"], traj["missile_y"], label=item["law_name"])
    target_traj = results[0]["trajectory"]
    ax.plot(target_traj["target_x"], target_traj["target_y"], linestyle="--", color="black", label="目标")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(cfg["title"])
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(cfg["trajectory_png"], dpi=200)
    plt.close(fig)


def render_forbidden_zone(results: list[dict], cfg: dict) -> None:
    """
    功能：绘制固定高度截面上的三点法攻击禁区示意图。
    参数：results 为不同发射高低角和过载约束组合的结果列表，cfg 为配置字典。
    返回：无。
    调用位置：main() 在攻击禁区实验分支中调用。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {True: "#2d8c4d", False: "#c24b37"}
    for item in results:
        x_pos = item["target_initial_x_m"]
        y_pos = item["target_initial_y_m"]
        feasible = item["intercepted"] and item["max_required_overload_g"] <= item["limit_overload_g"]
        ax.scatter(x_pos, y_pos, c=colors[feasible], s=20)
    ax.set_xlabel("目标初始 x / m")
    ax.set_ylabel("目标初始 y / m")
    ax.set_title(cfg["title"])
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(cfg["attack_png"], dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：读取 config.py 中的实验模式，执行三点法、前置量法及半前置量法仿真。
    参数：无。
    返回：无。
    调用位置：python main.py 程序入口。
    """

    ensure_directories()
    cfg = build_config()
    mode = cfg["mode"]
    results = []

    if mode == "gain_sweep":
        base = cfg["base_scenario"]
        baseline = cfg["baseline_gains"]
        for gain_value in cfg["gain_scan"]["k_e_values"]:
            gains = {"k_e": gain_value, "k_d": baseline["k_d"], "k_c": baseline["k_c"]}
            case = run_remote_case(
                case_name=f"k_e={gain_value}",
                law_name="三点法",
                lead_factor=0.0,
                gains=gains,
                missile_position=tuple(base["missile_position_m"]),
                target_position=tuple(base["target_position_m"]),
                missile_velocity=tuple(base["missile_velocity_mps"]),
                target_velocity=tuple(base["target_velocity_mps"]),
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            case["scan_group"] = "k_e"
            case["scan_value"] = gain_value
            results.append(case)
        for gain_value in cfg["gain_scan"]["k_d_values"]:
            gains = {"k_e": baseline["k_e"], "k_d": gain_value, "k_c": baseline["k_c"]}
            case = run_remote_case(
                case_name=f"k_d={gain_value}",
                law_name="三点法",
                lead_factor=0.0,
                gains=gains,
                missile_position=tuple(base["missile_position_m"]),
                target_position=tuple(base["target_position_m"]),
                missile_velocity=tuple(base["missile_velocity_mps"]),
                target_velocity=tuple(base["target_velocity_mps"]),
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            case["scan_group"] = "k_d"
            case["scan_value"] = gain_value
            results.append(case)
        for gain_value in cfg["gain_scan"]["k_c_values"]:
            gains = {"k_e": baseline["k_e"], "k_d": baseline["k_d"], "k_c": gain_value}
            case = run_remote_case(
                case_name=f"k_c={gain_value}",
                law_name="三点法",
                lead_factor=0.0,
                gains=gains,
                missile_position=tuple(base["missile_position_m"]),
                target_position=tuple(base["target_position_m"]),
                missile_velocity=tuple(base["missile_velocity_mps"]),
                target_velocity=tuple(base["target_velocity_mps"]),
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            case["scan_group"] = "k_c"
            case["scan_value"] = gain_value
            results.append(case)

        fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=False)
        for axis, group_name in zip(axes, ("k_e", "k_d", "k_c")):
            subset = [item for item in results if item["scan_group"] == group_name]
            axis.plot([item["scan_value"] for item in subset], [item["max_required_overload_g"] for item in subset], marker="o", label="最大需用过载")
            axis.plot([item["scan_value"] for item in subset], [item["miss_distance_m"] for item in subset], marker="s", label="脱靶量")
            axis.grid(True, linestyle="--", alpha=0.4)
            axis.set_title(group_name)
            axis.legend()
        fig.tight_layout()
        fig.savefig(cfg["metric_png"], dpi=200)
        plt.close(fig)

    elif mode == "law_compare_elevation":
        for case_info in cfg["cases"]:
            for law_name, lead_factor in cfg["law_map"].items():
                case = run_remote_case(
                    case_name=f"{law_name}-{case_info['elevation_deg']}",
                    law_name=law_name,
                    lead_factor=lead_factor,
                    gains=cfg["baseline_gains"],
                    missile_position=tuple(case_info["missile_position_m"]),
                    target_position=tuple(case_info["target_position_m"]),
                    missile_velocity=tuple(case_info["missile_velocity_mps"]),
                    target_velocity=tuple(case_info["target_velocity_mps"]),
                    max_overload_g=cfg["max_overload_g"],
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                )
                case["elevation_deg"] = case_info["elevation_deg"]
                results.append(case)
        render_method_compare(results, "elevation_deg", cfg)

    elif mode == "law_compare_maneuver":
        base = cfg["base_scenario"]
        for target_normal_g in cfg["target_normal_g_values"]:
            for law_name, lead_factor in cfg["law_map"].items():
                case = run_remote_case(
                    case_name=f"{law_name}-{target_normal_g}",
                    law_name=law_name,
                    lead_factor=lead_factor,
                    gains=cfg["baseline_gains"],
                    missile_position=tuple(base["missile_position_m"]),
                    target_position=tuple(base["target_position_m"]),
                    missile_velocity=tuple(base["missile_velocity_mps"]),
                    target_velocity=tuple(base["target_velocity_mps"]),
                    max_overload_g=cfg["max_overload_g"],
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                    target_normal_g=target_normal_g,
                )
                case["target_normal_g"] = target_normal_g
                results.append(case)
        render_method_compare(results, "target_normal_g", cfg)

    elif mode == "forbidden_zone":
        for limit_overload_g in cfg["limit_overload_values_g"]:
            for elevation_deg in cfg["elevation_values_deg"]:
                theta = math.radians(elevation_deg)
                x_target = cfg["target_altitude_m"] / max(math.tan(theta), 1e-6)
                target_position = (x_target, cfg["target_altitude_m"])
                missile_velocity = (
                    cfg["missile_speed_mps"] * math.cos(theta),
                    cfg["missile_speed_mps"] * math.sin(theta),
                )
                case = run_remote_case(
                    case_name=f"n={limit_overload_g},e={elevation_deg}",
                    law_name="三点法",
                    lead_factor=0.0,
                    gains=cfg["baseline_gains"],
                    missile_position=(0.0, 0.0),
                    target_position=target_position,
                    missile_velocity=missile_velocity,
                    target_velocity=tuple(cfg["target_velocity_mps"]),
                    max_overload_g=limit_overload_g,
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                )
                case["limit_overload_g"] = limit_overload_g
                case["elevation_deg"] = elevation_deg
                case["target_initial_x_m"] = round(x_target, 6)
                case["target_initial_y_m"] = cfg["target_altitude_m"]
                results.append(case)
        render_forbidden_zone(results, cfg)

    elif mode == "attitude_compare":
        base = cfg["base_scenario"]
        ideal_case = run_remote_case(
            case_name="无姿态回路",
            law_name="三点法",
            lead_factor=0.0,
            gains=cfg["baseline_gains"],
            missile_position=tuple(base["missile_position_m"]),
            target_position=tuple(base["target_position_m"]),
            missile_velocity=tuple(base["missile_velocity_mps"]),
            target_velocity=tuple(base["target_velocity_mps"]),
            max_overload_g=cfg["max_overload_g"],
            dt=cfg["dt"],
            t_max_s=cfg["t_max_s"],
            hit_radius_m=cfg["hit_radius_m"],
        )
        loop_case = run_remote_case(
            case_name="二阶姿态回路",
            law_name="三点法",
            lead_factor=0.0,
            gains=cfg["baseline_gains"],
            missile_position=tuple(base["missile_position_m"]),
            target_position=tuple(base["target_position_m"]),
            missile_velocity=tuple(base["missile_velocity_mps"]),
            target_velocity=tuple(base["target_velocity_mps"]),
            max_overload_g=cfg["max_overload_g"],
            dt=cfg["dt"],
            t_max_s=cfg["t_max_s"],
            hit_radius_m=cfg["hit_radius_m"],
            enable_attitude_loop=True,
            zeta=cfg["attitude_loop"]["zeta"],
            omega_n=cfg["attitude_loop"]["omega_n"],
        )
        results = [ideal_case, loop_case]

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for item in results:
            traj = item["trajectory"]
            axes[0].plot(traj["missile_x"], traj["missile_y"], label=item["case_name"])
        target_traj = results[0]["trajectory"]
        axes[0].plot(target_traj["target_x"], target_traj["target_y"], linestyle="--", color="black", label="目标")
        axes[0].set_xlabel("x / m")
        axes[0].set_ylabel("y / m")
        axes[0].set_title("弹道对比")
        axes[0].grid(True, linestyle="--", alpha=0.4)
        axes[0].legend()
        for item in results:
            traj = item["trajectory"]
            axes[1].plot(traj["time_s"], traj["required_g"], label=f"{item['case_name']}-需用过载")
            axes[1].plot(traj["time_s"], traj["actual_g"], linestyle="--", label=f"{item['case_name']}-实际过载")
        axes[1].set_xlabel("t / s")
        axes[1].set_ylabel("过载 / g")
        axes[1].set_title("姿态回路过载时程")
        axes[1].grid(True, linestyle="--", alpha=0.4)
        axes[1].legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(cfg["trajectory_png"], dpi=200)
        plt.close(fig)

    else:
        raise ValueError(f"未支持的实验模式: {mode}")

    summary_rows = [{key: value for key, value in item.items() if key != "trajectory"} for item in results]
    write_rows(summary_rows, cfg["summary_csv"])
    save_json({"title": cfg["title"], "mode": mode, "results": summary_rows}, cfg["detail_json"])
    print(f"实验完成，结果已保存到: {cfg['save_dir']}")


if __name__ == "__main__":
    main()
