import pandas as pd
import numpy as np
from ETc_cal import ETc
from PM_et0 import ET0_PM
def run (file, crop='corn', start=None ,end=None, output=None):
    df = pd.read_csv(file)
    df['DATE'] = pd.to_datetime(df['YEAR'].astype(str) + '-' + df['DOY'].astype(str), format='%Y-%j')
    df['ET0'] = ET0_PM(u2 = df['WS2M'],
          Tma = df['T2M_MAX'],
          Tmi = df['T2M_MIN'],
          RH = df['RH2M'],
          z = 1100,
          Rs = df['ALLSKY_SFC_SW_DWN'],
          lat = 38.2 * np.pi / 180,
          J = df['DOY'],
          P = None
        )
    clac = ETc(crop_type=crop)
    result = clac.calculate(df=df,  date_col='DATE', et0_col='ET0')
    if start:
        result = result[result['DATE'] >= pd.to_datetime(start)]
    if end:
        result = result[result['DATE'] <= pd.to_datetime(end)]
    if output:
        result.to_csv(output, index=False)
    return result
