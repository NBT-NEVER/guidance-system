# _*_coding:UTF-8_*_
"""
开发者: OpenAI Codex
文件名: main.py
生成时间: 2026-06-03 15:59:50
文件名: main.py
功能说明: 追踪法实验主程序 / Main entry for tracking-guidance experiment.
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

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
    功能：将任意角度限制到 [-pi, pi]，避免角度跳变影响导引计算。
    参数：angle 为待处理角度，单位 rad。
    返回：限制后的角度，单位 rad。
    调用位置：run_tracking_case() 与作图前的辅助处理。
    """

    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def write_rows(rows: list[dict], file_path) -> None:
    """
    功能：把实验统计结果写入 UTF-8 CSV 表格。
    参数：rows 为结果字典列表，file_path 为目标文件路径。
    返回：无。
    调用位置：main() 在每个实验分支结束后保存结果表。
    """

    if not rows:
        return
    with open(file_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_json(payload: dict, file_path) -> None:
    """
    功能：把实验摘要和关键元数据写入 JSON，便于后续复查。
    参数：payload 为可序列化字典，file_path 为目标文件路径。
    返回：无。
    调用位置：main() 保存图表后同步导出结构化摘要。
    """

    with open(file_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def run_tracking_case(
    case_name: str,
    missile_speed_mps: float,
    target_speed_mps: float,
    initial_range_m: float,
    initial_los_deg: float,
    target_heading_deg: float,
    max_overload_g: float,
    dt: float,
    t_max_s: float,
    hit_radius_m: float,
    enable_attitude_loop: bool = False,
    zeta: float = 0.707,
    omega_n: float = 10.0,
) -> dict:
    """
    功能：执行单个追踪法工况的数值积分，输出弹道、过载和脱靶量。
    参数：包含速度、初始距离、视线角、过载上限和姿态回路参数等单工况信息。
    返回：含轨迹点、最大需用过载、实际过载、脱靶量和命中标记的结果字典。
    调用位置：main() 中的速度比扫描、视线角扫描、攻击区扫描与姿态回路对比。
    """

    x_m, y_m = 0.0, 0.0
    los0 = math.radians(initial_los_deg)
    x_t = initial_range_m * math.cos(los0)
    y_t = initial_range_m * math.sin(los0)
    gamma = los0
    target_heading = math.radians(target_heading_deg)
    overload_state_g = 0.0
    overload_rate_g = 0.0
    min_range = initial_range_m
    max_required_g = 0.0
    max_actual_g = 0.0
    saturation_steps = 0
    flight_time_s = 0.0
    intercepted = False
    required_history = []
    actual_history = []
    time_history = []
    missile_x = [x_m]
    missile_y = [y_m]
    target_x = [x_t]
    target_y = [y_t]

    for step in range(int(t_max_s / dt)):
        rel_x = x_t - x_m
        rel_y = y_t - y_m
        rel_range = math.hypot(rel_x, rel_y)
        min_range = min(min_range, rel_range)
        if rel_range <= hit_radius_m:
            intercepted = True
            flight_time_s = step * dt
            break

        desired_heading = math.atan2(rel_y, rel_x)
        heading_error = wrap_to_pi(desired_heading - gamma)
        gamma_dot_cmd = heading_error / dt
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

        closing_speed = (rel_x * (target_speed_mps * math.cos(target_heading) - missile_speed_mps * math.cos(gamma)) + rel_y * (target_speed_mps * math.sin(target_heading) - missile_speed_mps * math.sin(gamma))) / max(rel_range, 1.0)
        if step > 10 and closing_speed > 0.0 and rel_range > min_range + 1.0:
            break

    return {
        "case_name": case_name,
        "missile_speed_mps": round(missile_speed_mps, 3),
        "target_speed_mps": round(target_speed_mps, 3),
        "initial_range_m": round(initial_range_m, 3),
        "initial_los_deg": round(initial_los_deg, 3),
        "max_required_overload_g": round(max_required_g, 6),
        "max_actual_overload_g": round(max_actual_g, 6),
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


def render_sweep_plot(results: list[dict], value_key: str, value_label: str, cfg: dict) -> None:
    """
    功能：为扫描类实验绘制弹道对比图和指标曲线图。
    参数：results 为工况结果列表，value_key 为横轴字段名，value_label 为横轴中文标签。
    返回：无。
    调用位置：main() 在速度比、视线角和初始距离实验结束后统一调用。
    """

    fig, ax = plt.subplots(figsize=(9, 6))
    for item in results:
        traj = item["trajectory"]
        ax.plot(traj["missile_x"], traj["missile_y"], label=f"{value_label}={item[value_key]}")
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

    x_values = [item[value_key] for item in results]
    need_g = [item["max_required_overload_g"] for item in results]
    miss = [item["miss_distance_m"] for item in results]
    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)
    axes[0].plot(x_values, need_g, marker="o")
    axes[0].axhline(cfg["max_overload_g"], color="red", linestyle="--", label="可用过载上限")
    axes[0].set_ylabel("最大需用过载 / g")
    axes[0].grid(True, linestyle="--", alpha=0.4)
    axes[0].legend()
    axes[1].plot(x_values, miss, marker="s", color="#b54d1a")
    axes[1].set_xlabel(value_label)
    axes[1].set_ylabel("脱靶量 / m")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(cfg["metric_png"], dpi=200)
    plt.close(fig)


def render_attack_zone(results: list[dict], cfg: dict) -> None:
    """
    功能：把追踪法允许攻击区扫描结果绘成二维散点图。
    参数：results 为不同初始距离和视线角组合下的仿真结果列表，cfg 为配置字典。
    返回：无。
    调用位置：main() 在允许攻击区实验分支中保存图形。
    """

    good_x = []
    good_y = []
    bad_x = []
    bad_y = []
    for item in results:
        radius = item["initial_range_m"]
        angle = math.radians(item["initial_los_deg"])
        x_pos = radius * math.cos(angle)
        y_pos = radius * math.sin(angle)
        feasible = item["intercepted"] and item["max_required_overload_g"] <= cfg["max_overload_g"]
        if feasible:
            good_x.append(x_pos)
            good_y.append(y_pos)
        else:
            bad_x.append(x_pos)
            bad_y.append(y_pos)

    fig, ax = plt.subplots(figsize=(9, 6))
    if good_x:
        ax.scatter(good_x, good_y, c="#2d8c4d", s=18, label="允许攻击区")
    if bad_x:
        ax.scatter(bad_x, bad_y, c="#c24b37", s=18, label="攻击禁区")
    ax.set_xlabel("目标初始 x / m")
    ax.set_ylabel("目标初始 y / m")
    ax.set_title(cfg["title"])
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    fig.tight_layout()
    fig.savefig(cfg["attack_png"], dpi=200)
    plt.close(fig)


def render_attitude_compare(results: list[dict], cfg: dict) -> None:
    """
    功能：对比无姿态回路和二阶姿态回路条件下的追踪法弹道与过载。
    参数：results 为两组工况的结果列表，cfg 为配置字典。
    返回：无。
    调用位置：main() 在姿态回路实验分支中保存两类图形。
    """

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
    axes[1].set_title("过载时程")
    axes[1].grid(True, linestyle="--", alpha=0.4)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(cfg["trajectory_png"], dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：读取 config.py 中的实验模式，执行对应的追踪法仿真并导出图表。
    参数：无。
    返回：无。
    调用位置：python main.py 统一入口。
    """

    ensure_directories()
    cfg = build_config()
    mode = cfg["mode"]
    results = []

    if mode == "speed_ratio_sweep":
        target_speed = cfg["base_scenario"]["target_speed_mps"]
        for ratio in cfg["speed_ratio_values"]:
            case = run_tracking_case(
                case_name=f"P={ratio}",
                missile_speed_mps=ratio * target_speed,
                target_speed_mps=target_speed,
                initial_range_m=cfg["base_scenario"]["initial_range_m"],
                initial_los_deg=cfg["base_scenario"]["initial_los_deg"],
                target_heading_deg=cfg["base_scenario"]["target_heading_deg"],
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            case["speed_ratio"] = ratio
            results.append(case)
        render_sweep_plot(results, "speed_ratio", "速度比 P", cfg)

    elif mode == "los_angle_sweep":
        for los_deg in cfg["initial_los_values_deg"]:
            case = run_tracking_case(
                case_name=f"q0={los_deg}deg",
                missile_speed_mps=cfg["base_scenario"]["missile_speed_mps"],
                target_speed_mps=cfg["base_scenario"]["target_speed_mps"],
                initial_range_m=cfg["base_scenario"]["initial_range_m"],
                initial_los_deg=los_deg,
                target_heading_deg=cfg["base_scenario"]["target_heading_deg"],
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            case["initial_los_deg"] = los_deg
            results.append(case)
        render_sweep_plot(results, "initial_los_deg", "初始视线角 / deg", cfg)

    elif mode == "range_sweep":
        for radius in cfg["initial_range_values_m"]:
            case = run_tracking_case(
                case_name=f"R0={radius}",
                missile_speed_mps=cfg["base_scenario"]["missile_speed_mps"],
                target_speed_mps=cfg["base_scenario"]["target_speed_mps"],
                initial_range_m=radius,
                initial_los_deg=cfg["base_scenario"]["initial_los_deg"],
                target_heading_deg=cfg["base_scenario"]["target_heading_deg"],
                max_overload_g=cfg["max_overload_g"],
                dt=cfg["dt"],
                t_max_s=cfg["t_max_s"],
                hit_radius_m=cfg["hit_radius_m"],
            )
            case["initial_range_m"] = radius
            results.append(case)
        render_sweep_plot(results, "initial_range_m", "初始弹目距离 / m", cfg)

    elif mode == "attack_zone":
        for radius in cfg["attack_zone_scan"]["range_values_m"]:
            for los_deg in cfg["attack_zone_scan"]["los_values_deg"]:
                case = run_tracking_case(
                    case_name=f"R={radius},q={los_deg}",
                    missile_speed_mps=cfg["base_scenario"]["missile_speed_mps"],
                    target_speed_mps=cfg["base_scenario"]["target_speed_mps"],
                    initial_range_m=radius,
                    initial_los_deg=los_deg,
                    target_heading_deg=cfg["base_scenario"]["target_heading_deg"],
                    max_overload_g=cfg["max_overload_g"],
                    dt=cfg["dt"],
                    t_max_s=cfg["t_max_s"],
                    hit_radius_m=cfg["hit_radius_m"],
                )
                case["initial_range_m"] = radius
                case["initial_los_deg"] = los_deg
                results.append(case)
        render_attack_zone(results, cfg)

    elif mode == "attitude_compare":
        base = cfg["base_scenario"]
        ideal_case = run_tracking_case(
            case_name="无姿态回路",
            missile_speed_mps=base["missile_speed_mps"],
            target_speed_mps=base["target_speed_mps"],
            initial_range_m=base["initial_range_m"],
            initial_los_deg=base["initial_los_deg"],
            target_heading_deg=base["target_heading_deg"],
            max_overload_g=cfg["max_overload_g"],
            dt=cfg["dt"],
            t_max_s=cfg["t_max_s"],
            hit_radius_m=cfg["hit_radius_m"],
        )
        loop_case = run_tracking_case(
            case_name="二阶姿态回路",
            missile_speed_mps=base["missile_speed_mps"],
            target_speed_mps=base["target_speed_mps"],
            initial_range_m=base["initial_range_m"],
            initial_los_deg=base["initial_los_deg"],
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
        render_attitude_compare(results, cfg)

    else:
        raise ValueError(f"未支持的实验模式: {mode}")

    summary_rows = []
    for item in results:
        row = {key: value for key, value in item.items() if key != "trajectory"}
        summary_rows.append(row)
    write_rows(summary_rows, cfg["summary_csv"])
    save_json({"title": cfg["title"], "mode": mode, "results": summary_rows}, cfg["detail_json"])
    print(f"实验完成，结果已保存到: {cfg['save_dir']}")


if __name__ == "__main__":
    main()
