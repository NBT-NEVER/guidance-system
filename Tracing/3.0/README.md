# 实验 3.0：追踪法中初始距离对拦截过程的影响

## 1. 实验内容

本实验研究纯追踪法在不同初始弹目距离 \(R_0\) 下的拦截过程。导弹与目标速度保持不变，只改变初始距离，考察其对飞行时间、需用过载和脱靶量的影响。

本版本仅实现“初始距离扫描”这一独立实验，不包含其余版本的切换逻辑。

## 2. 文件组成

```text
3.0
├─ config.py
├─ main.py
├─ README.md
└─ requirements.txt
```

## 3. 数学模型

### 3.1 初始位置

给定固定初始视线角 \(q_0\)，目标初始位置由不同的 \(R_0\) 决定：

\[
x_T(0)=R_0\cos q_0,\qquad y_T(0)=R_0\sin q_0
\]

### 3.2 纯追踪法指令关系

导弹瞬时指向目标当前位置，因此：

\[
\gamma_c=\operatorname{atan2}(y_T-y_M,\ x_T-x_M)
\]

\[
e_\gamma=\gamma_c-\gamma
\]

\[
\dot{\gamma}_c \approx \frac{e_\gamma}{\Delta t}
\]

\[
n_c=\frac{V_M\dot{\gamma}_c}{g}
\]

实际过载进行饱和限制：

\[
n=\operatorname{sat}(n_c,\ -n_{\max},\ n_{\max})
\]

### 3.3 运动积分

导弹运动学方程：

\[
\gamma_{k+1}=\gamma_k+\frac{ng}{V_M}\Delta t
\]

\[
x_{M,k+1}=x_{M,k}+V_M\cos\gamma_k\Delta t
\]

\[
y_{M,k+1}=y_{M,k}+V_M\sin\gamma_k\Delta t
\]

目标仍按匀速直线飞行：

\[
x_{T,k+1}=x_{T,k}+V_T\cos\psi_T\Delta t,\qquad
y_{T,k+1}=y_{T,k}+V_T\sin\psi_T\Delta t
\]

## 4. 程序实现流程

1. 在 `config.py` 中给出一组初始距离数组。
2. `main.py` 逐个读取不同初始距离并建立目标初始位置。
3. 在 `main()` 内直接执行离散积分。
4. 记录最大需用过载、最大实际过载、最小弹目距离、飞行时间和过载饱和比例。
5. 输出汇总表，并绘制轨迹图和统计图。

## 5. 输出文件

- `outputs/tables/summary.csv`
- `outputs/tables/summary.json`
- `outputs/figures/trajectory.png`
- `outputs/figures/metrics.png`

其中：

- `trajectory.png` 展示不同初始距离下的导弹轨迹。
- `metrics.png` 展示初始距离与最大需用过载、飞行时间的关系。

## 6. 运行方法

```bash
python main.py
```

## 7. 结果分析重点

- 初始距离越大，通常飞行时间越长，累计转向过程也更明显。
- 若距离增大但速度条件不变，导弹可能需要更长时间逐步修正航向。
- 当初始距离较大时，路径长度增加，过载积累特性与近距离情形会不同。
