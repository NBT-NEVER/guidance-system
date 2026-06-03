# 实验 5.0：带姿态回路的三点法拦截对比

## 1. 实验内容

本实验在三点法条件下，引入二阶姿态回路，比较理想过载建立和实际存在动态滞后的拦截效果。它用于说明外层地面站制导与内层姿态控制之间的耦合关系。

## 2. 关键公式

三点法参考线取为：

\[
\theta_{ref}=\theta_t
\]

外层制导律：

\[
\dot{\gamma}_c=-\left(k_e\frac{e}{R_t}+k_d\frac{\dot e}{V_M}+k_c\dot{\theta}_{ref}\right)
,\qquad
n_c=\frac{V_M\dot{\gamma}_c}{g}
\]

内层姿态回路采用二阶系统：

\[
\ddot{n}+2\zeta\omega_n\dot{n}+\omega_n^2 n=\omega_n^2 n_c
\]

## 3. 程序流程

1. 固定三点法参数和初始阵位。
2. 分别计算无姿态回路与带姿态回路两种工况。
3. 在 `main()` 内直接完成外层制导和内层动态积分。
4. 输出脱靶量、飞行时间和轨迹对比图。

## 4. 输出文件

- `outputs/tables/summary.csv`
- `outputs/tables/summary.json`
- `outputs/figures/trajectory.png`

## 5. 运行方法

```bash
python main.py
```

## 6. 结果观察重点

- 姿态回路滞后会削弱三点法对参考线的快速贴合能力。
- 实际过载建立变慢后，轨迹会更滞后，脱靶量可能增大。
- 该实验说明了地面站制导算法和飞行器控制动态不能分开孤立分析。
