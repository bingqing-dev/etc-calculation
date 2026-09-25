import numpy as np
def ET0_PM(u2, Tma, Tmi, RH, z, Rs, lat, J ,P = None):
    """
    基于 FAO-56 Penman-Monteith 公式计算参考作物蒸散量 (ET0)。
    
    参数说明 (单位必须严格匹配):
    --------------------------------
    u2   : 2米处风速 (m/s)
    Tma  : 日最高气温 (°C)
    Tmi  : 日最低气温 (°C)
    RH   : 相对湿度 (%)
    P    : 大气压 (kPa). 若为 None, 则根据海拔 z 自动估算.
    z    : 海拔高度 (m). 默认 0.
    Rs   : 太阳辐射 (MJ/m²/day).
    lat  : 纬度 (弧度 radians). 注意：如果是角度需先转换 np.radians(degrees).
    J    : 一年中的第几天 (1-365/366).
    
    返回:
    --------------------------------
    ET0  : 参考作物蒸散量 (mm/day). 若计算结果为负，强制归零.
    """
    if P is None:
        P = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    G = 0
    #日平均气温
    T = (Tma + Tmi) / 2
    #日平均饱和水汽压
    e0ma = 0.6108 * np.exp((17.27 * Tma) / (Tma + 237.3))
    e0mi = 0.6108 * np.exp((17.27 * Tmi) / (Tmi + 237.3))
    es = (e0ma + e0mi) / 2
    #饱和水汽压曲线斜率
    delta = (4098 * es) / ((T + 237.3) ** 2)
    #实际水汽压
    ea = es * (RH / 100)
    #干湿表常数
    gamma = 0.665e-3 * P
    #净短波辐射
    Rns = (1 - 0.23) * Rs
    #===========================================
    #净长波辐射___处理
    #===========================================
    
    #温度项#
    sigma = 4.903e-9                   #根据FAO-56手册
    Rnl_temp = sigma * (((Tma + 273.15) ** 4) + ((Tmi + 273.15) ** 4)) / 2
    
    ##水汽压项##
    Rnl_ea = 0.34 - (0.14 * np.sqrt(ea))
    
    ##辐射项##
    Gsc = 0.0820  # 太阳常数 (MJ/(m²·min))
    
    # 太阳赤纬 (弧度)
    declin = 0.409 * np.sin(2 * np.pi * J / 365 - 1.39)
    
    # 地球-太阳距离修正系数
    dr = 1 + 0.033 * np.cos(2 * np.pi * J / 365)
    
    # 日没时角 (弧度)
    cos_ws = -np.tan(lat) * np.tan(declin)
    cos_ws = np.clip(cos_ws, -1, 1)  # 避免超出定义域
    ws = np.arccos(cos_ws)
    
    # 天文辐射
    Ra = (24 * 60 / np.pi) * Gsc * dr * (
        ws * np.sin(lat) * np.sin(declin) +
        np.cos(lat) * np.cos(declin) * np.sin(ws))
    
    Rso = (0.75 + (2e-5 * z)) * Ra
    Rnl_rad = (1.35 * Rs / Rso) - 0.35
    Rnl_rad = np.clip(Rnl_rad, 0.05, 1.0) # FAO 建议

    #净长波总式
    Rnl = Rnl_temp * Rnl_ea * Rnl_rad
    #净辐射
    Rn = Rns - Rnl
    ##总方程##
    ET0_so = (0.408 * delta * (Rn - G)) + (gamma * (900 / (T + 273)) * u2 * (es - ea))
    ET0_ma = delta + gamma * (1 + (0.34 * u2))
    ET0 = ET0_so / ET0_ma
    ET0 = np.maximum(0,ET0)
    return ET0