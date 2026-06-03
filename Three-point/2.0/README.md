# 实验 2.0：三点法、前置量法与半前置量法对比

## 1. 实验内容

本实验比较三种地面站约束制导思想：

- 三点法
- 前置量法
- 半前置量法

三者的共同目标都是让导弹尽量沿地面站到目标的参考线运动，但前置量法会提前估计目标未来位置，半前置量法则只加入一半前置补偿。实验通过多个初始高低角工况，对比三种方法的需用过载、末端过载和脱靶量。

## 2. 模型公式

地面站到目标的视线角：

\[
\theta_t=\operatorname{atan2}(y_T,\ x_T)
\]

目标视线角速度：

\[
\dot{\theta}_t=\frac{x_T\dot{y}_T-y_T\dot{x}_T}{x_T^2+y_T^2}
\]

预计剩余时间：

\[
t_{go}=\frac{R_{MT}}{V_c}
\]

参考线角度写成：

\[
\theta_{ref}=\theta_t+C_f\dot{\theta}_t t_{go}
\]

其中：

- \(C_f=0\) 对应三点法；
- \(C_f=1\) 对应前置量法；
- \(C_f=0.5\) 对应半前置量法。

导弹相对参考线的线偏差：

\[
e=x_M\sin\theta_{ref}-y_M\cos\theta_{ref}
\]

制导指令采用线偏差、线偏差变化率和参考线转动项共同构成：

\[
\dot{\gamma}_c=-\left(k_e\frac{e}{R_t}+k_d\frac{\dot e}{V_M}+k_c\dot{\theta}_{ref}\right)
\]

\[
n_c=\frac{V_M\dot{\gamma}_c}{g}
\]

## 3. 程序流程

1. 固定三组增益 \(k_e,k_d,k_c\)。
2. 读取多个初始高低角工况。
3. 每个工况下分别计算三点法、前置量法和半前置量法。
4. 在 `main()` 内直接完成参考线生成、线偏差计算和导弹积分。
5. 输出对比表和图像。

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

- 当前置量增大时，导弹会更早修正航向，但需用过载也可能上升。
- 三点法响应相对保守，前置量法响应更积极。
- 半前置量法通常在过载需求和脱靶量之间提供折中。
