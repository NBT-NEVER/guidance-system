# 实验 3.0：目标机动条件下三种地面站制导方法对比

## 1. 实验内容

本实验在目标进行法向机动的情况下，对比三点法、前置量法和半前置量法。与实验 2.0 相比，这里不再改变初始高低角，而是固定初始工况，观察目标机动增强后，不同参考线构造方式对制导效果的影响。

## 2. 模型要点

三种方法的区别仍在参考线角度：

\[
\theta_{ref}=\theta_t+C_f\dot{\theta}_t t_{go}
\]

其中 \(C_f\) 分别取 0、1、0.5。

目标做法向机动时，其航向角满足：

\[
\psi_{T,k+1}=\psi_{T,k}+\frac{n_T g}{V_T}\Delta t
\]

导弹控制律仍为：

\[
\dot{\gamma}_c=-\left(k_e\frac{e}{R_t}+k_d\frac{\dot e}{V_M}+k_c\dot{\theta}_{ref}\right)
,\qquad
n_c=\frac{V_M\dot{\gamma}_c}{g}
\]

## 3. 程序流程

1. 固定初始阵位和导弹、目标速度。
2. 扫描不同目标机动过载。
3. 对每个机动过载分别计算三点法、前置量法、半前置量法。
4. 输出最大需用过载、末端过载和脱靶量。

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

- 目标机动增强后，三点法通常更容易出现滞后。
- 前置量法会更积极地提前修正，但也可能提高过载需求。
- 半前置量法在机动条件下仍然常表现出折中效果。
