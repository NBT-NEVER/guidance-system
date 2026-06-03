# 实验 5.0：带姿态回路的追踪法拦截对比

## 1. 实验内容

本实验在纯追踪法基础上，引入二阶姿态回路，比较“理想过载立即建立”和“存在姿态动态滞后”两种情况的拦截效果。该实验用于说明：即使外层制导律相同，内环动态也会改变实际轨迹和末端效果。

本版本只做姿态回路对比，不保留其他实验接口。

## 2. 文件组成

```text
5.0
├─ config.py
├─ main.py
├─ README.md
└─ requirements.txt
```

## 3. 基本模型

### 3.1 外层追踪法指令

外层控制仍采用纯追踪法：

\[
\gamma_c=\operatorname{atan2}(y_T-y_M,\ x_T-x_M)
\]

\[
\dot{\gamma}_c \approx \frac{\gamma_c-\gamma}{\Delta t}
\]

\[
n_c=\frac{V_M\dot{\gamma}_c}{g}
\]

### 3.2 无姿态回路情况

无姿态回路时，默认实际过载直接等于饱和后的指令过载：

\[
n=\operatorname{sat}(n_c,\ -n_{\max},\ n_{\max})
\]

### 3.3 二阶姿态回路情况

带姿态回路时，实际过载不再瞬时建立，而满足二阶系统：

\[
\ddot{n}+2\zeta\omega_n\dot{n}+\omega_n^2 n=\omega_n^2 n_c
\]

程序中采用离散积分：

\[
\ddot{n}=\omega_n^2(n_c-n)-2\zeta\omega_n\dot{n}
\]

\[
\dot{n}_{k+1}=\dot{n}_k+\ddot{n}\Delta t
\]

\[
n_{k+1}=n_k+\dot{n}_{k+1}\Delta t
\]

之后再做过载限幅。

### 3.4 导弹运动积分

\[
\gamma_{k+1}=\gamma_k+\frac{ng}{V_M}\Delta t
\]

\[
x_{M,k+1}=x_{M,k}+V_M\cos\gamma_k\Delta t,\qquad
y_{M,k+1}=y_{M,k}+V_M\sin\gamma_k\Delta t
\]

## 4. 程序流程

1. 读取固定初始条件。
2. 分别计算两组情况：无姿态回路、二阶姿态回路。
3. 在 `main()` 内直接完成离散积分。
4. 记录最大需用过载、最大实际过载、脱靶量和飞行时间。
5. 输出对比表并绘制轨迹图。

## 5. 输出文件

- `outputs/tables/summary.csv`
- `outputs/tables/summary.json`
- `outputs/figures/trajectory.png`

其中 `trajectory.png` 用于直接比较两种内环动态下的导弹轨迹差异。

## 6. 运行方法

```bash
python main.py
```

## 7. 结果观察重点

- 带姿态回路时，实际过载建立存在滞后，因此轨迹会比理想情况更“迟缓”。
- 若外层指令变化快，二阶回路可能造成跟踪误差扩大，从而使末端脱靶量增加。
- 该实验说明了制导回路与控制回路耦合分析的重要性。
