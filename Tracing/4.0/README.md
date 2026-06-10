# 实验 4.0：追踪法允许攻击区判定

## 1. 实验内容

本实验采用二维平面网格扫描的方法，判定在纯追踪法条件下，哪些初始弹目距离与初始视线角组合能够实现有效拦截。这里的“允许攻击区”指的是在给定速度条件和最大过载约束下，导弹能够进入命中半径，并且所需最大过载不超过限制的初始区域。

本实验是独立版本，只完成攻击区判定，不含其他实验逻辑。

## 2. 文件组成

```text
4.0
├─ config.py
├─ main.py
├─ README.md
└─ requirements.txt
```

## 3. 判定思路

### 3.1 扫描变量

本实验对下列初始条件做网格扫描：

- 初始弹目距离 \(R_0\)
  渲染：R₀
- 初始视线角 \(q_0\)
  渲染：q₀

其中，初始弹目距离仍按 `config.py` 中的 `RANGE_VALUES_M` 离散取值；初始视线角采样方式则由 `LOS_SAMPLING_MODE` 统一控制。

当 `LOS_SAMPLING_MODE = "uniform_angle"` 时，程序对所有半径统一使用固定角度步长 `UNIFORM_LOS_STEP_DEG`，这对应之前的均匀采样方案。

当 `LOS_SAMPLING_MODE = "adaptive_arc"` 时，程序使用 `ATTACK_ZONE_POINT_SPACING_M` 作为目标弧向点间距，在每一个固定半径圆环上动态计算对应的角度采样点列，因此半径越大，角度点数越多。

目标初始坐标仍由

\[
x_T(0)=R_0\cos q_0,\qquad y_T(0)=R_0\sin q_0
\]

渲染：x_T(0) = R₀ cos q₀，y_T(0) = R₀ sin q₀

给出。

### 3.2 纯追踪法控制

每个网格点都按纯追踪法积分：

\[
\gamma_c=\operatorname{atan2}(y_T-y_M,\ x_T-x_M)
\]

渲染：γ_c = atan2(y_T - y_M，x_T - x_M)

\[
n_c=\frac{V_M}{g}\cdot\frac{\gamma_c-\gamma}{\Delta t}
\]

渲染：n_c = (V_M / g) · [(γ_c - γ) / Δt]

并对过载做饱和限制：

\[
n=\operatorname{sat}(n_c,\ -n_{\max},\ n_{\max})
\]

渲染：n = sat(n_c，-n_max，n_max)

### 3.3 攻击区判定标准

对每组初始条件，程序记录：

- 是否进入命中半径；
- 最大需用过载是否超过上限。

若同时满足：

\[
R_{\min}\le R_{\text{hit}}
\]

渲染：R_min ≤ R_hit

并且

\[
n_{\max,\text{required}}\le n_{\max}
\]

渲染：n_max,required ≤ n_max

则判定该点属于允许攻击区。

## 4. 程序流程

1. 从 `config.py` 读取距离网格 `RANGE_VALUES_M`、采样模式 `LOS_SAMPLING_MODE` 以及对应的采样参数。
2. 若采样模式为 `uniform_angle`，则对所有半径统一使用固定角度步长 `UNIFORM_LOS_STEP_DEG`；若采样模式为 `adaptive_arc`，则对每一个初始距离 \(R_0\) 按半圆弧长 \(\pi R_0\) 动态生成该半径下的初始视线角采样点。
3. 在 `main()` 中逐点执行独立追踪法积分。
4. 记录最小距离、最大需用过载、飞行时间和命中结果。
5. 将所有真实计算点写入 `summary.csv` 与 `summary.json`。
6. 直接根据这些真实计算点绘制直角坐标攻击区分布图，不再在绘图阶段额外补点。

## 5. 输出文件

- `outputs/tables/summary.csv`
- `outputs/tables/summary.json`
- `outputs/figures/attack_zone.png`
- `outputs/figures/attack_zone_cartesian_miss.png`

其中 `attack_zone.png` 中：

- 绿色点表示满足允许攻击区条件；
- 红色点表示不能满足命中与过载约束。

`attack_zone_cartesian_miss.png` 中：

- 蓝色空心圆表示可击中区域；
- 红色叉号表示不可击中区域；
- 黑色方块表示导弹初始位置。

## 6. 运行方法

```bash
python main.py
```

## 7. 采样改进总结

本实验的直角坐标攻击区图经历了三步改进。

第一步，程序最初对所有半径统一使用固定角度步长。这样做在极坐标下比较直观，但映射到直角坐标后会出现一个明显问题：半径越大，同样的角度间隔对应的圆弧长度越长，因此外围圆环上的点会越来越稀，看起来像是“从中心到外圈密度逐渐下降”。

第二步，曾尝试只在绘图阶段做补点，也就是保留原始计算结果不变，再在图上按相邻角度样本之间插值加密。这种方法能改善视觉效果，但图上的一部分点并不是实际仿真点，图形展示与 `summary.csv`、`summary.json` 中的真实计算样本并不完全一致。

第三步，也是当前默认采用的方法，是把密度调整前移到计算阶段。程序现在对每一个初始距离 \(R_0\) 都按弧长自适应生成视线角采样点，使外围半径自动拥有更多角度样本。这样一来，图上的每一个点都对应一次真实仿真，绘图阶段只负责直接展示结果，不再做后处理补点，图和表保持一致。

当前程序已经保留了两种方案，并支持一键切换：只需在 `config.py` 中修改 `LOS_SAMPLING_MODE` 即可在“之前的均匀角度采样”与“按半径自适应采样”之间切换。

- 当 `LOS_SAMPLING_MODE = "uniform_angle"` 时，由 `UNIFORM_LOS_STEP_DEG` 控制均匀角度步长。
- 当 `LOS_SAMPLING_MODE = "adaptive_arc"` 时，由 `ATTACK_ZONE_POINT_SPACING_M` 控制沿圆弧方向的目标点间距；数值越小，单个圆环上的采样点越多，攻击区边界会更细；数值越大，计算点越少，运行速度更快，但图上会变得更稀。

## 8. 结果观察重点

- 初始距离过大时，纯追踪法往往需要更长路径，攻击区会收缩。
- 初始视线角偏大时，导弹初始转向负担增加，可能导致需用过载超限。
- 攻击区图本质上反映了速度条件、几何条件和过载约束共同作用后的可拦截范围。
