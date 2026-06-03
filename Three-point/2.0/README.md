# 实验二（困难）：对比三点法、前置量法与半前置量法

## 1. 实验任务
当前目录对应《guidance-system.pdf》中的 **实验二（困难）：对比三点法、前置量法与半前置量法**。三点法部分的教材截图在 OCR 之后有缺符号和少量错字，所以这里把核心思路保留为“地面站—目标—导弹同线约束”，再用一个写得更清楚的归一化线偏差模型落成代码。

- 实验目的：在不同初始高低角条件下，对比三点法、前置量法和半前置量法的过载与脱靶特性。
- 重点扫描量：初始高低角 / deg = 30，45，60，75
- 默认时间步长：`0.01 s`
- 当前实验的主要过载约束：`20.0 g`

## 2. 建模假设
- 地面制导站固定在坐标原点，作战平面取二维 `x-y` 平面。
- 三点法用“导弹尽量贴着地面站到目标的参考线飞行”来表达。
- 前置量法和半前置量法用 `C_f = 1`、`C_f = 0.5` 的前置系数区分，参考线角度写成 `θ_ref = θ_t + C_f θ̇_t t_go`。
- 题目没有给出完整的姿态回路参数时，二阶环节统一按 `ξ = 0.707, ω = 10` 处理。

## 3. 数学模型
公式展示：

$$
\theta_t = \operatorname{atan2}(y_T, x_T)
$$

这个角度是地面站看到目标的视线角，也是三点法里参考线的基础量。

其中：
- `θ_t`：地面站到目标的视线角。
- `(x_T, y_T)`：目标相对地面站的位置。

$$
\theta_{ref} = \theta_t + C_f \dot{\theta}_t t_{go}
$$

当 `C_f = 0` 时得到三点法；`C_f = 1` 是前置量法；`C_f = 0.5` 是半前置量法。

$$
e = x_M \sin \theta_{ref} - y_M \cos \theta_{ref}
$$

这里的 `e` 表示导弹相对参考线的线偏差。代码里没有再引入复杂的中间变量，而是直接拿这条线偏差和它的变化率生成导引指令。

$$
\dot{\gamma}_c = -\left(k_e \frac{e}{R_t} + k_d \frac{\dot e}{V_M} + k_c \dot{\theta}_{ref}\right),
\qquad
n_c = \frac{V_M \dot{\gamma}_c}{g}
$$

这个式子把题目要求的三项量都写进去了：线偏差、线偏差微分和动态误差补偿。这样虽然比课件截图更工程化，但每一项都能在代码里直接找到。

LaTeX 代码：

```latex
\theta_t = \operatorname{atan2}(y_T, x_T)
\theta_{ref} = \theta_t + C_f \dot{\theta}_t t_{go}
e = x_M \sin \theta_{ref} - y_M \cos \theta_{ref}
\dot{\gamma}_c = -\left(k_e \frac{e}{R_t} + k_d \frac{\dot e}{V_M} + k_c \dot{\theta}_{ref}\right)
n_c = \frac{V_M \dot{\gamma}_c}{g}
```

## 4. 数值求解流程
1. 初始化地面站、目标和导弹的坐标与速度矢量。
2. 由目标坐标计算当前视线角 `θ_t` 和视线角速率 `θ̇_t`。
3. 根据三点法、前置量法或半前置量法生成参考线角 `θ_ref`。
4. 计算导弹对参考线的线偏差 `e` 及其差分近似 `ė`。
5. 用 `k_e`、`k_d`、`k_c` 组合出法向过载指令。
6. 若题目要求考虑姿态回路，就先经过二阶环节，再把真实过载换算成弹道角变化。
7. 更新导弹与目标位置，记录最大需用过载、命中点过载和脱靶量。

## 5. 代码结构
```text
.
├─config.py
├─main.py
├─README.md
└─requirements.txt
```

- `config.py`：保存题目参数、增益扫描范围和输出路径。
- `main.py`：完成三点法、前置量法、半前置量法的积分与作图。
- `README.md`：说明题目、公式、假设和使用方式。
- `requirements.txt`：列出 `numpy` 与 `matplotlib`。

调用关系：`main.py -> build_config() -> run_remote_case() -> 保存 CSV/JSON/PNG`。

## 6. 运行方式
```bash
python main.py
```

## 7. 输出文件
- `outputs/tables/summary.csv`：参数扫描、方法对比或攻击禁区统计表。
- `outputs/tables/summary.json`：同一批结果的结构化版本。
- `outputs/figures/trajectory.png`：典型弹道图。
- `outputs/figures/metrics.png`：最大需用过载、命中点过载和脱靶量曲线。
- `outputs/figures/attack_zone.png`：实验 4 的攻击禁区图。

## 8. 当前实验模式
- 模式：`law_compare_elevation`
- 题目要求中的核心观察量：这里把 PDF 表中的四组初始位置和速度原样写进 config，再对三种方法逐组比较。
- 需要改初始阵位或增益时，优先改 `config.py` 里的字典和列表，不要先动主求解循环。

## 9. 说明
三点法这一组里，原参考资料的课件图片在 OCR 之后有缺字和公式残缺。这里没有回避这个问题，而是把等效控制量、线偏差和前置量假设明确写出来。这样做的目的不是“重新发明公式”，而是让代码、README 和后续实验分析都能自洽，也方便你后面根据老师给的课堂推导再逐项替换。
