# 实验 4.0：三点法攻击禁区判定

## 1. 实验内容

本实验基于三点法，在不同发射高低角和不同过载上限约束下，判定哪些组合无法完成拦截，从而形成“攻击禁区”概念。与允许攻击区不同，这里更强调由于过载不足或几何条件不利而导致的不可达区域。

## 2. 判定思路

三点法采用：

\[
\theta_{ref}=\theta_t
\]

并利用线偏差控制律：

\[
\dot{\gamma}_c=-\left(k_e\frac{e}{R_t}+k_d\frac{\dot e}{V_M}+k_c\dot{\theta}_{ref}\right)
,\qquad
n_c=\frac{V_M\dot{\gamma}_c}{g}
\]

对每个发射高低角与过载上限组合：

1. 建立导弹和目标初始几何关系；
2. 执行离散积分；
3. 判断是否命中；
4. 判断最大需用过载是否超过允许上限。

若不能满足命中与过载要求，则视为禁区点。

## 3. 输出文件

- `outputs/tables/summary.csv`
- `outputs/tables/summary.json`
- `outputs/figures/attack_zone.png`

## 4. 运行方法

```bash
python main.py
```

## 5. 结果观察重点

- 允许过载越低，禁区范围通常越大。
- 发射高低角过小或过大时，都可能导致不利几何条件。
- 该图可以直接说明三点法在受限控制能力下的使用边界。
