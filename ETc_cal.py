import numpy as np
import pandas as pd
from datetime import datetime


class ETc:
    """
    基于单作物系数法的作物蒸散量(ETc)计算
    可跨年，忽略闰年

    参数说明(单位需严格匹配):
    --------------------------------
    
    --------------------------------
    """
    def __init__(self, crop_type='corn', ET0_file=None, date_col='date', ET0_col='eto'):
        """
        :param crop_type:作物类型
        :param ET0_file: 数据文件路径
        :param date_col: 儒略日列
        :param ET0_col: ET0列名
        """
        self.crop_type = crop_type
        self.ET0_file = ET0_file
        self.date_col = date_col
        self.ET0_col = ET0_col
        if ET0_file:
            self.df = pd.read_csv(ET0_file)
            self.df[date_col] = pd.to_datetime(self.df[date_col])
        else:
            self.df = None

        """
        定义作物系数(单作物系数法)
        """

        self.crop_params = {
            'corn': {
                'name': '玉米',
                'growth_period': {
                    'start': (4, 20),
                    'end': (9, 30),
                    'Kc_ini': 0.3,
                    'Kc_mid': 1.2,
                    'Kc_end': 0.35,
                    'L_ini': 30,
                    'L_dev': 50,
                    'L_mid': 50,
                    'L_end': 30
                }
            },
            'wheat': {'name': '小麦',
                      'growth_period': {
                          'start': (10, 1),
                          'end': (6, 15),
                          'Kc_ini': 0.4,
                          'Kc_mid': 1.15,
                          'Kc_end': 0.4,
                          'L_ini': 30,
                          'L_dev': 50,
                          'L_mid': 50,
                          'L_end': 30
                      }
                      }
        }

    def date_to_doy(self, date):
        """将日期转换为儒略日"""
        return int(date.strftime('%j'))

    def get_Kc_from_params(self, date, params):  # 依赖 def __init__中crop_type的字典
        """从crop_params 获得Kc"""

        doy = self.date_to_doy(date)
        year = date.year


        # 计算doy
        start_date = datetime(year, params['start'][0], params['start'][1])
        end_date = datetime(year, params['end'][0], params['end'][1])

        start_doy = self.date_to_doy(start_date)
        end_doy = self.date_to_doy(end_date)
        # 跨年判断分支
        cross_year = (end_doy < start_doy)
        if cross_year:
            end_date= end_date.replace(year = end_date.year + 1)
            end_doy = self.date_to_doy(end_date) + 365
            if doy < start_doy:
                start_date = start_date.replace(year = start_date.year - 1)
                start_doy = self.date_to_doy(start_date)
        if doy < start_doy:
            doy = doy + 365

        # 阶段划分
        ini_end = start_doy + params['L_ini']
        dev_end = ini_end + params['L_dev']
        mid_end = end_doy - params['L_end']
        mid_start = mid_end - params['L_mid']

        Kc_ini = params['Kc_ini']
        Kc_mid = params['Kc_mid']
        Kc_end = params['Kc_end']

        if doy < start_doy or doy > end_doy:
            return 0

        elif doy <= ini_end:
            return params['Kc_ini']

        elif doy <= dev_end:
            # 发展期线性插值
            ratio0 = (doy - ini_end) / params['L_dev']
            return Kc_ini + (Kc_mid - Kc_ini) * ratio0

        elif mid_start <= doy <= mid_end:
            return Kc_mid

        elif  mid_end <= doy <= end_doy:
            # 后期线性插值
            ratio = (doy - mid_end) / params['L_end']
            return Kc_mid - (Kc_mid - Kc_end) * ratio

    def get_Kc(self, date):  # 依赖 def get_Kc_from_param

        if self.crop_type not in self.crop_params:
            raise ValueError(f'未知作物类型{self.crop_type}')

        params = self.crop_params[self.crop_type]['growth_period']
        return self.get_Kc_from_params(date, params)

    def calculate(self, df=None, et0_col=None, date_col=None):  # 无依赖，可单独使用
        """
        计算ETc:
        :param df:可单独使用DataFrame,或默认使用初始化数据
        :param et0_col: ET0列名
        :param date_col: 日期列名
        :return:
        DataFrame，包含Kc与ETc列
        """
        if df is None:
            df = self.df
        if df is None:
            raise ValueError("请提供数据源或传入DataFrame")

        et0_col = et0_col or self.ET0_col
        date_col = date_col or self.date_col

        result = df.copy()

        result['Kc'] = result[date_col].apply(self.get_Kc)
        result['ETc'] = result['Kc'] * result[et0_col]
        return result

    def save(self, output_file, df=None, **kwargs):
        """保存结果"""
        result = self.calculate(df, **kwargs)
        filtered_result = result[result['Kc'] > 0].copy()
        if filtered_result.empty:
            print('警告：计算结果为空，未找到生长季内日期！请检查日期范围。')
        else:
            filtered_result.to_csv(output_file, index=False)
            print(f"结果已保存至{output_file}")
        return filtered_result

    def summary(self, df=None, **kwargs):
        """
        打印 ETc 计算结果摘要
        包括：总 ETc、平均 ETc、最大 ETc、有作物覆盖天数、月统计
        """
        result_origin = self.calculate(df, **kwargs)
        result = result_origin[result_origin['Kc'] > 0]

        print("\n" + "=" * 50)
        print(f"作物类型: {self.crop_params[self.crop_type]['name']}")
        print(f"数据时段: {result[self.date_col].min().date()} 至 {result[self.date_col].max().date()}")
        print("=" * 50)

        print(f"总 ETc: {result['ETc'].sum():.1f} mm")
        print(f"平均 ETc: {result['ETc'].mean():.2f} mm/d")
        print(f"最大 ETc: {result['ETc'].max():.2f} mm/d")
        print(f"有作物覆盖天数: {(result['Kc'] > 0).sum()} 天")

        # 按月份统计
        result['month'] = result[self.date_col].dt.month
        monthly = result.groupby('month')['ETc'].sum()
        print("\n逐月 ETc 统计:")
        for month, etc in monthly.items():
            print(f"  {month}月: {etc:.1f} mm")

        # 按生长阶段统计（如果日期覆盖完整生长季）
        if (result['Kc'] > 0).sum() > 0:
            print("\n按生长阶段统计:")

            # 获取生长阶段划分的儒略日边界
            params = self.crop_params[self.crop_type]['growth_period']
            year = result[self.date_col].iloc[0].year
            start_date = datetime(year, params['start'][0], params['start'][1])
            end_date = datetime(year, params['end'][0], params['end'][1])

            start_doy = self.date_to_doy(start_date)
            end_doy = self.date_to_doy(end_date)

            # 跨年判断，与 get_Kc_from_params 保持一致
            cross_year = (end_doy < start_doy)

            # 根据儒略日划分阶段
            doy_series = result[self.date_col].apply(self.date_to_doy)

            # 统一相对天数坐标
            adjusted_doy = doy_series.copy()
            if cross_year:
                adjusted_doy[doy_series < start_doy] += 365

            # 阶段划分（使用统一后的相对天数）
            ini_end_doy = start_doy + params['L_ini']
            dev_end_doy = ini_end_doy + params['L_dev']
            mid_end_doy = dev_end_doy + params['L_mid']

            ini_mask = (adjusted_doy >= start_doy) & (adjusted_doy < ini_end_doy)
            dev_mask = (adjusted_doy >= ini_end_doy) & (adjusted_doy < dev_end_doy)
            mid_mask = (adjusted_doy >= dev_end_doy) & (adjusted_doy < mid_end_doy)
            end_mask = (adjusted_doy >= mid_end_doy) & (adjusted_doy <= (
                    start_doy + params['L_ini'] + params['L_dev'] + params['L_mid'] + params['L_end']))

            if ini_mask.any():
                print(f"  初始期: {result.loc[ini_mask, 'ETc'].sum():.1f} mm")
            if dev_mask.any():
                print(f"  发展期: {result.loc[dev_mask, 'ETc'].sum():.1f} mm")
            if mid_mask.any():
                print(f"  中期: {result.loc[mid_mask, 'ETc'].sum():.1f} mm")
            if end_mask.any():
                print(f"  后期: {result.loc[end_mask, 'ETc'].sum():.1f} mm")

        print("=" * 50 + "\n")
        return result