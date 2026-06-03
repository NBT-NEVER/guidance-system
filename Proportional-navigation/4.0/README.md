# 实验 4.0：比例导航法对目标机动的适应性

## 1. 实验内容

本实验研究目标进行法向机动时，比例导航法的拦截性能如何变化。目标不再保持固定航向，而是按给定法向过载连续转弯。实验目的是观察比例导航法面对机动目标时，对需用过载、轨迹弯曲程度和脱靶量的响应。

## 2. 关键公式

比例导航指令：

\[
n_c=\frac{K V_c \dot{\lambda}}{g}
\]

其中：

\[
\dot{\lambda}=\frac{x_r\dot{y}_r-y_r\dot{x}_r}{r^2},\qquad
V_c=-\frac{x_r\dot{x}_r+y_r\dot{y}_r}{r}
\]

目标航向角在存在法向机动时满足：

\[
\psi_{T,k+1}=\psi_{T,k}+\frac{n_T g}{V_T}\Delta t
\]

其中 \(n_T\) 为目标机动过载。

## 3. 实现流程

1. 固定导弹速度、目标速度和导航比。
2. 扫描不同目标法向过载。
3. 每个工况下执行完整比例导航积分。
4. 更新目标航向角，使目标持续转弯。
5. 统计最大需用过载、脱靶量和飞行时间。

## 4. 输出文件

- `outputs/tables/summary.csv`
- `outputs/tables/summary.json`
- `outputs/figures/trajectory.png`
- `outputs/figures/metrics.png`

## 5. 运行方法

```bash
python main.py
```

## 6. 结果观察重点

- 目标机动越强，导弹通常需要更大的法向过载才能跟上视线旋转。
- 当目标机动水平升高后，比例导航的脱靶量可能明显上升。
- 该实验可用来观察固定导航比对目标机动的适应边界。
