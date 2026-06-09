# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
开发时间: 2026-06-09 00:00:00
文件名: main.py
功能说明: 比例导引法允许攻击区计算主程序
版本号：5.0
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from config import (
    ANGLE_VALUES_DEG,  # 发射方位角扫描序列，单位为 deg。
    ATTACK_PNG,  # 直角坐标攻击区图输出文件路径。
    DT,  # 离散积分步长，单位为 s。
    MAX_OVERLOAD_G,  # 导弹最大可用法向过载，单位为 g。
    MISS_DISTANCE_THRESHOLD_M,  # 攻击区判定脱靶量阈值，单位为 m。
    MISSILE_SPEED_MPS,  # 导弹飞行速度，单位为 m/s。
    NAVIGATION_RATIO,  # 比例导引导航比 N。
    PARAMETER_ATTACK_PNG,  # 参数平面攻击区图输出文件路径。
    RADIUS_VALUES_M,  # 发射半径扫描序列，单位为 m。
    SAVE_DIR,  # 当前实验输出根目录。
    SUMMARY_CSV,  # 汇总结果 CSV 文件路径。
    SUMMARY_JSON,  # 汇总结果 JSON 文件路径。
    TARGET_HEADING_DEG,  # 目标航向角，单位为 deg。
    TARGET_POSITION_M,  # 目标初始位置坐标，单位为 m。
    TARGET_SPEED_MPS,  # 目标飞行速度，单位为 m/s。
    TITLE,  # 图表标题文本。
    T_MAX_S,  # 单条轨迹最大仿真时长，单位为 s。
    ensure_directories,  # 创建输出目录结构的初始化函数。
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
    调用位置：main() 统计结束后。
    """

    with open(SUMMARY_CSV, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(SUMMARY_JSON, "w", encoding="utf-8") as handle:
        json.dump({"title": TITLE, "results": rows}, handle, ensure_ascii=False, indent=2)


def estimate_segment_min_range(
    rel_x_start: float,
    rel_y_start: float,
    rel_x_end: float,
    rel_y_end: float,
) -> tuple[float, float]:
    """
    功能：估计单个时间步内弹目相对位移线段的最小距离。
    参数：起点与终点相对坐标分量。
    返回：最小距离与最小距离对应的线段比例系数。
    调用位置：main() 单步积分结束后。
    """

    delta_x = rel_x_end - rel_x_start
    delta_y = rel_y_end - rel_y_start
    segment_norm_sq = delta_x**2 + delta_y**2
    if segment_norm_sq <= 1e-12:
        return math.hypot(rel_x_start, rel_y_start), 0.0

    ratio = -(rel_x_start * delta_x + rel_y_start * delta_y) / segment_norm_sq
    ratio = max(0.0, min(1.0, ratio))
    closest_x = rel_x_start + ratio * delta_x
    closest_y = rel_y_start + ratio * delta_y
    return math.hypot(closest_x, closest_y), ratio


def plot_attack_zone(results: list[dict]) -> None:
    """
    功能：绘制直角坐标系下的允许攻击区图。
    参数：results 为网格扫描结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    feasible_x = [item["launch_x_m"] for item in results if item["feasible"]]
    feasible_y = [item["launch_y_m"] for item in results if item["feasible"]]
    axis_limit = max(RADIUS_VALUES_M) * 1.05

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(feasible_x, feasible_y, s=10, c="#e53935", marker=".")
    ax.scatter(TARGET_POSITION_M[0], TARGET_POSITION_M[1], c="black", s=20, marker="s")
    ax.set_xlabel("导弹发射点 x 坐标 / m")
    ax.set_ylabel("导弹发射点 y 坐标 / m")
    ax.set_title(f"{TITLE}（a_max = {MAX_OVERLOAD_G:.0f}g，N = {NAVIGATION_RATIO:.0f}）")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-axis_limit, axis_limit)
    ax.set_ylim(-axis_limit, axis_limit)
    fig.tight_layout()
    fig.savefig(ATTACK_PNG, dpi=200)
    plt.close(fig)


def plot_parameter_attack_zone(results: list[dict]) -> None:
    """
    功能：绘制发射半径与发射方位角参数平面上的允许攻击区图。
    参数：results 为网格扫描结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    feasible_angle = [item["launch_angle_deg"] for item in results if item["feasible"]]
    feasible_radius = [item["launch_radius_m"] for item in results if item["feasible"]]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(feasible_angle, feasible_radius, s=10, c="#e53935", marker=".")
    ax.set_xlabel("发射方位角 / deg")
    ax.set_ylabel("发射半径 / m")
    ax.set_title(f"{TITLE}：参数平面攻击区")
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(PARAMETER_ATTACK_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行比例导引法实验 5.0 的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    # 创建输出目录，避免后续保存表格和图像时因目录不存在而报错。
    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    # 目标航向固定沿 x 轴正方向，目标速度分量可在循环外直接计算。
    target_heading = math.radians(TARGET_HEADING_DEG)
    target_vx = TARGET_SPEED_MPS * math.cos(target_heading)
    target_vy = TARGET_SPEED_MPS * math.sin(target_heading)

    # results 用于保存整个攻击区网格中每一个初始发射点的判定结果。
    results = []

    # 双层循环分别扫描发射半径 rm 和发射方位角 qm。
    # 每一组 (rm, qm) 都对应攻击区图上的一个离散采样点。
    for launch_radius_m in RADIUS_VALUES_M:
        for launch_angle_deg in ANGLE_VALUES_DEG:
            # 根据极坐标关系建立导弹初始位置，目标初始位置固定在原点。
            launch_angle_rad = math.radians(launch_angle_deg)  # 发射方位角 qm，单位为 rad。
            launch_x_m = launch_radius_m * math.cos(launch_angle_rad)  # 导弹初始 x 坐标，单位为 m。
            launch_y_m = launch_radius_m * math.sin(launch_angle_rad)  # 导弹初始 y 坐标，单位为 m。
            x_m = launch_x_m  # 导弹当前 x 坐标，单位为 m。
            y_m = launch_y_m  # 导弹当前 y 坐标，单位为 m。
            x_t, y_t = TARGET_POSITION_M  # 目标当前坐标，单位为 m。

            # 导弹初始速度方向始终对准目标初始位置。
            gamma = math.atan2(y_t - y_m, x_t - x_m)  # 导弹当前航向角，单位为 rad。

            # min_range 记录整个飞行过程中出现过的最小弹目距离。
            # 本实验的攻击区判定只依赖这一脱靶量是否小于 0.1 m。
            min_range = math.hypot(x_t - x_m, y_t - y_m)  # 当前这组条件下的最小弹目距离，单位为 m。

            # max_required_g 记录理论需用过载峰值，即未限幅前的控制需求。
            # max_actual_g 记录实际执行过载峰值，即饱和限制后的真实控制量。
            max_required_g = 0.0  # 理论需用过载峰值，单位为 g。
            max_actual_g = 0.0  # 实际执行过载峰值，单位为 g。

            # saturation_steps 用于统计过载触及上限的离散时刻数量。
            saturation_steps = 0  # 发生过载饱和的步数。
            flight_time_s = 0.0  # 当前轨迹累计飞行时间，单位为 s。
            intercepted = False  # 是否实现了脱靶量小于阈值的命中。

            # 采用固定步长 DT 做离散积分，最多积分到 T_MAX_S。
            for step in range(int(T_MAX_S / DT)):
                current_time_s = step * DT  # 当前离散步开始时刻，单位为 s。

                # 计算当前弹目相对位置向量 r = [x_T - x_M, y_T - y_M]。
                rel_x = x_t - x_m  # 弹目相对 x 位移，单位为 m。
                rel_y = y_t - y_m  # 弹目相对 y 位移，单位为 m。

                # 当前弹目距离 R = sqrt(rel_x^2 + rel_y^2)。
                rel_range = math.hypot(rel_x, rel_y)  # 当前弹目距离，单位为 m。
                min_range = min(min_range, rel_range)

                # 若离散时刻本身已进入脱靶量阈值，则可直接判定命中。
                if rel_range < MISS_DISTANCE_THRESHOLD_M:
                    intercepted = True
                    flight_time_s = current_time_s
                    break

                # 导弹与目标的速度由各自速度大小和当前航向角决定。
                vx_m = MISSILE_SPEED_MPS * math.cos(gamma)  # 导弹 x 方向速度，单位为 m/s。
                vy_m = MISSILE_SPEED_MPS * math.sin(gamma)  # 导弹 y 方向速度，单位为 m/s。

                # 相对速度向量 v_r = [vx_T - vx_M, vy_T - vy_M]。
                rel_vx = target_vx - vx_m  # 弹目相对 x 方向速度，单位为 m/s。
                rel_vy = target_vy - vy_m  # 弹目相对 y 方向速度，单位为 m/s。

                # 视线角速度 lambda_dot = (r_x * v_ry - r_y * v_rx) / R^2。
                los_rate = (rel_x * rel_vy - rel_y * rel_vx) / max(rel_range**2, 1e-12)  # 视线角速度，单位为 rad/s。

                # 闭合速度定义为 Vc = -(r · v_r) / |r|，Vc > 0 表示弹目距离正在减小。
                closing_speed = -(rel_x * rel_vx + rel_y * rel_vy) / max(rel_range, 1e-12)  # 当前闭合速度，单位为 m/s。

                # 比例导引指令满足 n_req = N * Vc * lambda_dot / g0。
                # 当 Vc 已经小于 0 时，说明当前轨迹正在张开，此时不再继续增加反向需用过载。
                required_g = NAVIGATION_RATIO * max(closing_speed, 0.0) * los_rate / G0  # 理论需用法向过载，单位为 g。

                # 实际法向过载受最大可用过载限制，需要做饱和限幅。
                actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))  # 限幅后的实际法向过载，单位为 g。
                if abs(required_g) > MAX_OVERLOAD_G:
                    saturation_steps += 1

                # 统计全过程中的峰值需用过载与峰值实际过载。
                max_required_g = max(max_required_g, abs(required_g))
                max_actual_g = max(max_actual_g, abs(actual_g))

                # 采用中点航向更新位置，可比简单前向欧拉更稳定。
                gamma_dot = actual_g * G0 / MISSILE_SPEED_MPS  # 导弹航向角变化率，单位为 rad/s。
                gamma_mid = gamma + 0.5 * gamma_dot * DT  # 单步中点航向角，单位为 rad。
                gamma_next = gamma + gamma_dot * DT  # 单步结束航向角，单位为 rad。

                x_m_next = x_m + MISSILE_SPEED_MPS * math.cos(gamma_mid) * DT  # 下一时刻导弹 x 坐标，单位为 m。
                y_m_next = y_m + MISSILE_SPEED_MPS * math.sin(gamma_mid) * DT  # 下一时刻导弹 y 坐标，单位为 m。
                x_t_next = x_t + target_vx * DT  # 下一时刻目标 x 坐标，单位为 m。
                y_t_next = y_t + target_vy * DT  # 下一时刻目标 y 坐标，单位为 m。

                # 仅用离散采样点最小距离会漏掉步间命中，这里按相对位移线段估计单步最小距离。
                rel_x_next = x_t_next - x_m_next  # 下一时刻弹目相对 x 位移，单位为 m。
                rel_y_next = y_t_next - y_m_next  # 下一时刻弹目相对 y 位移，单位为 m。
                segment_min_range, segment_ratio = estimate_segment_min_range(rel_x, rel_y, rel_x_next, rel_y_next)
                min_range = min(min_range, segment_min_range)

                # 若步间连续最小距离已满足脱靶量阈值，则记录该时刻并结束积分。
                if segment_min_range < MISS_DISTANCE_THRESHOLD_M:
                    intercepted = True
                    flight_time_s = current_time_s + segment_ratio * DT
                    break

                # 当前步未命中，则推进到下一时刻继续积分。
                x_m = x_m_next
                y_m = y_m_next
                x_t = x_t_next
                y_t = y_t_next
                gamma = gamma_next
                flight_time_s = current_time_s + DT

            # 攻击区可行性仅依据实际脱靶量是否小于 0.1 m。
            # 最大需用过载是本实验要求额外统计的指标，不再作为二次筛选条件。
            feasible = min_range < MISS_DISTANCE_THRESHOLD_M

            # 将当前这组初始发射条件对应的统计结果写入结果表。
            results.append(
                {
                    "launch_radius_m": launch_radius_m,  # 发射半径 rm，单位为 m。
                    "launch_angle_deg": launch_angle_deg,  # 发射方位角 qm，单位为 deg。
                    "launch_x_m": round(launch_x_m, 6),  # 导弹初始 x 坐标，单位为 m。
                    "launch_y_m": round(launch_y_m, 6),  # 导弹初始 y 坐标，单位为 m。
                    "max_required_overload_g": round(max_required_g, 6),  # 理论需用过载峰值，单位为 g。
                    "max_actual_overload_g": round(max_actual_g, 6),  # 实际执行过载峰值，单位为 g。
                    "miss_distance_m": round(min_range, 6),  # 全轨迹最小弹目距离，单位为 m。
                    "intercepted": intercepted,  # 是否实现脱靶量小于阈值的命中。
                    "flight_time_s": round(flight_time_s, 6),  # 轨迹累计飞行时间，单位为 s。
                    "saturation_ratio": round(saturation_steps / max(1, int(flight_time_s / DT) + 1), 6),  # 过载饱和步数占比。
                    "feasible": feasible,  # 是否属于允许攻击区。
                }
            )

    # 输出数值结果表，便于后续统计、复核和报告引用。
    write_summary(results)
    # 绘制直角坐标系下的允许攻击区图。
    plot_attack_zone(results)
    # 绘制参数平面上的允许攻击区图。
    plot_parameter_attack_zone(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
