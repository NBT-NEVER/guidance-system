# _*_coding:UTF-8_*_
"""
开发者: NBT
文件名: main.py
开发时间: 2026-06-03 00:00:00
文件名: main.py
功能说明:追踪法允许攻击区分析主程序
版本号：4.0
"""

import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

from config import (
    ATTACK_PNG,  # 允许攻击区散点图输出文件路径。
    CARTESIAN_MISS_PNG,  # 直角坐标攻击区图输出文件路径。
    DT,  # 离散积分步长，单位为 s。
    HIT_RADIUS_M,  # 命中判定半径，单位为 m。
    LOS_VALUES_DEG,  # 初始视线角扫描序列，单位为 deg。
    MAX_OVERLOAD_G,  # 导弹最大允许法向过载，单位为 g。
    MISSILE_SPEED_MPS,  # 导弹飞行速度，单位为 m/s。
    RANGE_VALUES_M,  # 初始弹目距离扫描序列，单位为 m。
    SAVE_DIR,  # 当前实验输出根目录。
    SUMMARY_CSV,  # 汇总结果 CSV 文件路径。
    SUMMARY_JSON,  # 汇总结果 JSON 文件路径。
    TARGET_HEADING_DEG,  # 目标航向角，单位为 deg。
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
    功能：绘制追踪法允许攻击区直角坐标系散点图。
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


def plot_cartesian_attack_zone(results: list[dict]) -> None:
    """
    功能：绘制极坐标允许攻击区。
    参数：results 为网格扫描结果列表。
    返回：无。
    调用位置：main() 统计完成后。
    """

    fig, ax = plt.subplots(figsize=(9, 9))
    hit_x: list[float] = []
    hit_y: list[float] = []
    miss_x: list[float] = []
    miss_y: list[float] = []
    max_range = 0.0

    for item in results:
        los_rad = math.radians(item["initial_los_deg"])
        x_pos = item["initial_range_m"] * math.cos(los_rad)
        y_pos = item["initial_range_m"] * math.sin(los_rad)

        # 当前程序扫描的是上半平面角度，这里通过关于 x 轴镜像，
        # 将同一组初始条件同时投影到上下两个角度位置。
        y_candidates = [y_pos] if abs(y_pos) < 1e-9 else [y_pos, -y_pos]

        for mirrored_y in y_candidates:
            if item["feasible"]:
                hit_x.append(x_pos)
                hit_y.append(mirrored_y)
            else:
                miss_x.append(x_pos)
                miss_y.append(mirrored_y)

        max_range = max(max_range, item["initial_range_m"])

    # 蓝色空心圆表示可击中初始条件。
    ax.scatter(hit_x, hit_y, s=44, facecolors="none", edgecolors="#1f4fe0", linewidths=1.0, marker="o")
    # 红色叉号表示不可击中初始条件。
    ax.scatter(miss_x, miss_y, s=20, c="#e53935", linewidths=0.9, marker="x")

    # 在原始判定点位置再叠加一个更小的中心点，突出每个离散样本的真实坐标。
    ax.scatter(hit_x, hit_y, s=7, c="#1f4fe0", marker="o")
    ax.scatter(miss_x, miss_y, s=7, c="#e53935", marker="o")
    ax.scatter(0.0, 0.0, c="black", s=22, marker="s")

    ax.set_xlabel("初始目标 x 坐标 / m")
    ax.set_ylabel("初始目标 y 坐标 / m")
    ax.set_title(f"{TITLE}：直角坐标可击中/不可击中分布")
    ax.set_aspect("equal", adjustable="box")
    axis_limit = max_range * 1.05
    ax.set_xlim(-axis_limit, axis_limit)
    ax.set_ylim(-axis_limit, axis_limit)
    ax.grid(True, linestyle="--", alpha=0.4)
    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markerfacecolor="none",
            markeredgecolor="#1f4fe0",
            markeredgewidth=1.0,
            markersize=7,
            label="可击中区域（蓝圈）",
        ),
        Line2D(
            [0],
            [0],
            marker="x",
            linestyle="None",
            color="#e53935",
            markersize=7,
            label="不可击中区域（红叉）",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            color="#1f4fe0",
            markersize=4,
            label="可击中中心点",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            color="#e53935",
            markersize=4,
            label="不可击中中心点",
        ),
        Line2D(
            [0],
            [0],
            marker="s",
            linestyle="None",
            color="black",
            markersize=5,
            label="导弹初始位置",
        ),
    ]
    ax.legend(handles=legend_handles, loc="upper right")
    fig.tight_layout()
    fig.savefig(CARTESIAN_MISS_PNG, dpi=200)
    plt.close(fig)


def main() -> None:
    """
    功能：执行追踪法实验 4.0 的全部计算、统计与绘图。
    参数：无。
    返回：无。
    调用位置：python main.py。
    """

    # 创建输出目录，避免后续保存表格和图像时因目录不存在而报错。
    ensure_directories()
    # 配置绘图字体与负号显示。
    configure_matplotlib()

    # results 用于保存整个攻击区网格中每一个初始条件点的判定结果。
    results = []

    # 双层循环分别扫描初始弹目距离 R0 和初始视线角 q0，
    # 每一组 (R0, q0) 都对应攻击区图上的一个离散采样点。
    for initial_range_m in RANGE_VALUES_M:
        for initial_los_deg in LOS_VALUES_DEG:
            # 建立二维平面直角坐标系，导弹初始位置固定在原点。
            x_m = 0.0  # 导弹当前 x 坐标，单位为 m。
            y_m = 0.0  # 导弹当前 y 坐标，单位为 m。

            # 将初始视线角从角度制转换为弧度制，便于参与三角函数计算。
            los0 = math.radians(initial_los_deg)  # 初始视线角 q0，对应目标相对导弹的初始方位角，单位为 rad。

            # 由极坐标关系得到目标初始坐标：
            # x_T(0) = R0 * cos(q0)
            # y_T(0) = R0 * sin(q0)
            x_t = initial_range_m * math.cos(los0)  # 目标当前 x 坐标，单位为 m。
            y_t = initial_range_m * math.sin(los0)  # 目标当前 y 坐标，单位为 m。

            # 追踪法假设导弹速度方向始终努力对准目标，
            # 这里将导弹初始航向角 gamma(0) 设为初始视线角 q0。
            gamma = los0  # 导弹当前航向角，单位为 rad。

            # 目标航向保持常值，后续按匀速直线运动更新位置。
            target_heading = math.radians(TARGET_HEADING_DEG)  # 目标航向角，单位为 rad。

            # min_range 记录整个飞行过程中出现过的最小弹目距离，
            # 它既可用于评价脱靶量，也可用于提前终止发散轨迹。
            min_range = initial_range_m  # 当前这组初始条件下的最小弹目距离，单位为 m。

            # max_required_g 记录理论需求过载峰值，即未限幅前的控制需求。
            # max_actual_g 记录实际执行过载峰值，即饱和限制后的真实控制量。
            max_required_g = 0.0  # 理论需求过载峰值，单位为 g。
            max_actual_g = 0.0  # 实际输出过载峰值，单位为 g。

            # saturation_steps 用于统计过载饱和的离散时刻数，
            # 便于后续估计控制指令触及极限的频繁程度。
            saturation_steps = 0  # 发生过载饱和的步数。
            flight_time_s = 0.0  # 当前轨迹已累计的飞行时间，单位为 s。
            intercepted = False  # 是否已经进入命中半径。

            # 采用固定步长 DT 做离散积分，最多积分到 T_MAX_S。
            for step in range(int(T_MAX_S / DT)):
                # 计算当前弹目相对位置向量 r = [x_T - x_M, y_T - y_M]。
                rel_x = x_t - x_m  # 弹目相对 x 位移，单位为 m。
                rel_y = y_t - y_m  # 弹目相对 y 位移，单位为 m。

                # 当前弹目距离 R = sqrt(rel_x^2 + rel_y^2)。
                rel_range = math.hypot(rel_x, rel_y)  # 当前弹目距离，单位为 m。

                # 持续刷新最小距离，用于脱靶量统计。
                min_range = min(min_range, rel_range)

                # 当最小距离进入命中半径时，认为本组初始条件实现拦截。
                if rel_range <= HIT_RADIUS_M:
                    intercepted = True
                    flight_time_s = step * DT
                    break

                # 期望航向角等于当前视线角：
                # gamma_c = atan2(y_T - y_M, x_T - x_M)。
                desired_heading = math.atan2(rel_y, rel_x)  # 期望航向角，即当前视线角，单位为 rad。

                # 航向误差 e_gamma = gamma_c - gamma。
                heading_error = desired_heading - gamma  # 期望航向与当前航向之间的误差，单位为 rad。

                # 将误差限制到 [-pi, pi]，确保导弹总是沿最短转向方向修正。
                while heading_error > math.pi:
                    heading_error -= 2.0 * math.pi
                while heading_error < -math.pi:
                    heading_error += 2.0 * math.pi

                # 这里采用离散一步逼近思想，
                # 将期望角速度近似写成 gamma_dot_cmd = e_gamma / DT。
                gamma_dot_cmd = heading_error / DT  # 指令航向角速度，单位为 rad/s。

                # 由平面转弯运动关系 a_n = V_M * gamma_dot，
                # 可得到需求法向过载：
                # n_req = a_n / g0 = V_M * gamma_dot_cmd / g0。
                required_g = MISSILE_SPEED_MPS * gamma_dot_cmd / G0  # 未限幅前的需求法向过载，单位为 g。

                # 实际过载受最大允许过载约束，需要做饱和限幅：
                # n_act = sat(n_req, -n_max, n_max)。
                actual_g = max(-MAX_OVERLOAD_G, min(MAX_OVERLOAD_G, required_g))  # 限幅后的实际法向过载，单位为 g。
                if abs(required_g) > MAX_OVERLOAD_G:
                    saturation_steps += 1

                # 根据实际过载反推实际航向角变化率：
                # gamma_dot = n_act * g0 / V_M。
                # 随后用前向欧拉法更新导弹和目标位置。
                gamma += actual_g * G0 / MISSILE_SPEED_MPS * DT
                #actual_g * G0 / MISSILE_SPEED_MPS = gamma_dot
                x_m += MISSILE_SPEED_MPS * math.cos(gamma) * DT
                y_m += MISSILE_SPEED_MPS * math.sin(gamma) * DT
                x_t += TARGET_SPEED_MPS * math.cos(target_heading) * DT
                y_t += TARGET_SPEED_MPS * math.sin(target_heading) * DT

                # 统计全过程中的峰值需求过载与峰值实际过载。
                max_required_g = max(max_required_g, abs(required_g))
                max_actual_g = max(max_actual_g, abs(actual_g))
                flight_time_s = step * DT

                # 闭合速度本质上是相对速度在当前视线方向上的投影：
                # V_c = (r · (V_T - V_M)) / |r|。
                # 若 V_c > 0，说明距离开始增大；再结合当前距离已明显大于最小距离，
                # 可以认为该轨迹已经越过最近点并进入发散阶段，提前结束可节省计算量。
                closing_speed = (
                    rel_x * (TARGET_SPEED_MPS * math.cos(target_heading) - MISSILE_SPEED_MPS * math.cos(gamma))
                    + rel_y * (TARGET_SPEED_MPS * math.sin(target_heading) - MISSILE_SPEED_MPS * math.sin(gamma))
                ) / max(rel_range, 1.0)  # 当前闭合速度，单位为 m/s。
                if step > 10 and closing_speed > 0.0 and rel_range > min_range + 1.0:
                    break

            # 攻击区可行性的判据包含两层：
            # 1. 实际进入命中半径；
            # 2. 理论需求过载峰值不超过允许上限。
            feasible = intercepted and max_required_g <= MAX_OVERLOAD_G
            # 将当前这一组初始条件对应的统计结果写入结果表，
            # 这些字段会同时输出到 summary.csv / summary.json，并被后续绘图函数读取。
            results.append(
                {
                    "initial_range_m": initial_range_m,  # 初始弹目距离 R0，即仿真开始时目标到导弹的直线距离，单位为 m。
                    "initial_los_deg": initial_los_deg,  # 初始视线角 q0，即目标相对导弹的初始方位角，单位为 deg。
                    "max_required_overload_g": round(max_required_g, 6),  # 理论需求过载峰值，即未经过载限幅前控制律要求的最大法向过载，单位为 g。
                    "max_actual_overload_g": round(max_actual_g, 6),  # 实际执行过载峰值，即经过 ±MAX_OVERLOAD_G 限幅后真正输出过的最大法向过载，单位为 g。
                    "miss_distance_m": round(min_range, 6),  # 最小弹目距离，即整个飞行过程中出现过的最近接距离；若未命中，它也可视为脱靶量，单位为 m。
                    "intercepted": intercepted,  # 是否命中：True 表示弹目距离曾进入命中半径 HIT_RADIUS_M，False 表示始终未进入命中半径。
                    "flight_time_s": round(flight_time_s, 6),  # 本组轨迹累计飞行时间；命中时表示命中时刻，未命中时表示仿真终止时刻，单位为 s。
                    "saturation_ratio": round(saturation_steps / max(1, int(flight_time_s / DT) + 1), 6),  # 过载饱和比例，即发生限幅的离散步数占总积分步数的比例，用于反映控制指令触及过载上限的频繁程度。
                    "feasible": feasible,  # 攻击区可行性判定：既要命中 intercepted=True，又要求理论需求过载峰值不超过允许上限 MAX_OVERLOAD_G。
                }
            )

    # 输出数值结果表，便于后续统计、复核和报告引用。
    write_summary(results)
    # 绘制当前实验的允许攻击区判定图。
    #plot_attack_zone(results)
    # 绘制极坐标初始条件映射到直角坐标后的脱靶量圆圈图。
    plot_cartesian_attack_zone(results)
    print(f"实验完成，结果已保存到 {SAVE_DIR}")


if __name__ == "__main__":
    main()
