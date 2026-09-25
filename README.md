# etc-calculation
Python tools for crop water requirement calculation
 # 作物需水量计算工具 (ET0 & ETc)

基于 FAO-56 标准，用 Python 实现参考蒸散量（ET₀）和作物需水量（ETc）的计算工具。

## 仓库结构

- `PM_et0.py`：参考蒸散量（ET₀）计算函数
  - 基于 FAO-56 Penman-Monteith 公式
  - 输入：温度、湿度、风速、辐射、海拔、纬度
  - 输出：逐日 ET₀ (mm/d)

- `ETc_cal.py`：作物需水量（ETc）计算类
  - 基于单作物系数法：ETc = Kc × ET₀
  - 支持玉米、小麦等作物
  - 支持跨年作物（如冬小麦）的生长季判断

## 数据验证

将自写 ET₀ 函数与 pyfao56 库（基于 ASCE 标准化参考蒸散量方程）在同一组气象数据上进行对比：

- 数据来源：NASA POWER 榆林地区 2023-2025 年逐日气象数据
- 对比结果：
  - R² = 0.99
  - RMSE < 0.2 mm/d
- 结论：自写函数与标准库输出高度一致，可用于后续作物需水量计算。

## 依赖

- Python 3.8+
- pandas
- numpy
- pyfao56（仅用于验证，非运行必需）

## 使用示例

```python
from PM_et0 import ET0_PM
from ETc_cal import ETc

# 计算 ET0
et0 = ET0_PM(u2=2.2, Tma=32.5, Tmi=18.2, RH=55, z=1100, Rs=24.5, lat=0.667, J=200)
print(et0)

# 计算 ETc
calc = ETc(crop_type='corn', ET0_file='corn_et0.csv', date_col='DATE', ET0_col='ET0')
calc.save('corn_etc.csv')

